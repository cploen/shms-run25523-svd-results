"""Fit SHMS xp, ytar, yp optics terms from a TFit ROOT tree.

The first four matrix powers are (xfp[m], xpfp, yfp[m], ypfp); the
fifth is xtar[m]. Only xtar-independent coefficients are solved. The
historical delta column and all xtar-dependent coefficients stay fixed.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import uproot


ROW = re.compile(r"^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+([0-9]{5})\s*$")
TARGETS = ("xptarT", "ytarT", "yptarT")
BASE = ("xfp", "xpfp", "yfp", "ypfp", "xtarT")
LABELS = {
    "foil": ("foil_rank", "relative_foil_rank"),
    "col": ("hole_col", "relative_hole_col"),
    "row": ("hole_row", "relative_hole_row"),
}


def read_matrix(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines(keepends=True)
    rows = []
    seen = set()
    for index, line in enumerate(lines):
        match = ROW.fullmatch(line.rstrip("\r\n"))
        if not match:
            continue
        power = match[5]
        if power in seen:
            raise ValueError(f"duplicate matrix power {power}")
        seen.add(power)
        try:
            values = np.array([float(match[i]) for i in range(1, 5)])
        except ValueError as exc:
            raise ValueError(f"invalid matrix row {index + 1}") from exc
        if not np.isfinite(values).all():
            raise ValueError(f"nonfinite matrix row {index + 1}")
        rows.append((index, power, values))
    if not rows:
        raise ValueError("matrix has no coefficient rows")
    return lines, rows


def _branch(tree, names):
    for name in names:
        if name in tree:
            return name
    raise ValueError(f"missing TFit branch: {' or '.join(names)}")


def read_tfit(path):
    with uproot.open(path, handler=uproot.source.file.MemmapSource) as root:
        if "TFit" not in root:
            raise ValueError("missing TFit tree")
        tree = root["TFit"]
        names = list(BASE) + list(TARGETS) + ["delta", "train"]
        mapping = {name: _branch(tree, (name,)) for name in names}
        mapping.update({name: _branch(tree, choices) for name, choices in LABELS.items()})
        if "fit_weight" in tree:
            mapping["fit_weight"] = "fit_weight"
        raw = tree.arrays(list(mapping.values()), library="np")
        data = {name: np.asarray(raw[source]) for name, source in mapping.items()}
    count = len(data["xfp"])
    if not count or any(len(value) != count or value.ndim != 1 for value in data.values()):
        raise ValueError("TFit must contain nonempty scalar branches with equal lengths")
    for name, values in data.items():
        if not np.isfinite(values).all():
            raise ValueError(f"nonfinite TFit branch: {name}")
    train = data["train"]
    if not np.isin(train, [0, 1]).all() or not np.any(train == 1) or not np.any(train == 0):
        raise ValueError("train must be binary with nonempty train and holdout sets")
    if "fit_weight" in data and np.any(data["fit_weight"] <= 0):
        raise ValueError("fit_weight must be positive")
    return data, mapping


def powers(data, terms):
    variables = np.column_stack(
        [data["xfp"] / 100, data["xpfp"], data["yfp"] / 100,
         data["ypfp"], data["xtarT"] / 100]
    )
    design = np.ones((len(variables), len(terms)), dtype=np.float64)
    for column, (_, power, _) in enumerate(terms):
        for axis, exponent in enumerate(power):
            if exponent != "0":
                design[:, column] *= variables[:, axis] ** int(exponent)
    return design


def weights(data, train, delta_bin_width):
    if "fit_weight" in data:
        weight = np.asarray(data["fit_weight"][train], dtype=np.float64)
        mode = "fit_weight branch"
    else:
        if delta_bin_width <= 0:
            raise ValueError("delta-bin-width must be positive")
        # Each occupied foil/hole/delta cell has the same total weight.
        cells = np.column_stack((data["foil"][train], data["col"][train],
                                 data["row"][train],
                                 np.floor(data["delta"][train] / delta_bin_width)))
        _, inverse, counts = np.unique(cells, axis=0, return_inverse=True, return_counts=True)
        weight = 1 / counts[inverse].astype(np.float64)
        mode = f"equal occupied foil-hole-{delta_bin_width:g}% delta cells"
    weight /= weight.mean()
    return weight, mode


def metrics(truth, predicted):
    residual = predicted - truth
    return {
        "count": int(len(residual)),
        "rmse": np.sqrt(np.mean(residual ** 2, axis=0)).tolist(),
        "median": np.median(residual, axis=0).tolist(),
        "abs_p95": np.quantile(np.abs(residual), 0.95, axis=0).tolist(),
    }


def fit(input_path, matrix_path, output_dir, rcond=1e-10, delta_bin_width=1.0,
        xptar_offset=-8.681269905e-4, yptar_offset=0.0):
    if not 0 < rcond < 1:
        raise ValueError("rcond must be between 0 and 1")
    if not np.isfinite([xptar_offset, yptar_offset]).all():
        raise ValueError("replay offsets must be finite")
    data, mapping = read_tfit(input_path)
    lines, existing = read_matrix(matrix_path)
    train = data["train"].astype(bool)
    holdout = ~train
    terms = list(existing)
    if "00000" not in {power for _, power, _ in terms}:
        terms.append((None, "00000", np.zeros(4)))
    fit_columns = [i for i, (_, power, _) in enumerate(terms) if power[-1] == "0"]
    fixed_columns = [i for i, (_, power, _) in enumerate(terms) if power[-1] != "0"]
    design = powers(data, terms)
    truth = np.column_stack((data["xptarT"], data["ytarT"] / 100, data["yptarT"]))
    replay_offset = np.array([xptar_offset, 0.0, yptar_offset])
    fixed = design[:, fixed_columns] @ np.stack([terms[i][2][:3] for i in fixed_columns]) if fixed_columns else np.zeros_like(truth)
    baseline = design @ np.stack([values[:3] for _, _, values in terms]) + replay_offset
    a = design[train][:, fit_columns]
    b = (truth - fixed - replay_offset)[train]
    weight, weight_mode = weights(data, train, delta_bin_width)
    scale = np.linalg.norm(a * np.sqrt(weight[:, None]), axis=0)
    if np.any(scale == 0):
        raise ValueError("zero design column; cannot fit requested matrix basis")
    weighted_a = a * (np.sqrt(weight[:, None]) / scale)
    solution, _, rank, singular = np.linalg.lstsq(weighted_a, b * np.sqrt(weight[:, None]), rcond=rcond)
    coefficients = solution / scale[:, None]
    fitted = design[:, fit_columns] @ coefficients + fixed + replay_offset
    fit_terms = {terms[i][1]: coefficients[j] for j, i in enumerate(fit_columns)}
    report = {
        "input_sha256": hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
        "base_matrix_sha256": hashlib.sha256(Path(matrix_path).read_bytes()).hexdigest(),
        "branches": mapping,
        "units": {"xptar": "slope", "ytar": "m", "yptar": "slope", "delta": "unchanged base fraction"},
        "replay_offsets": {"xptar": xptar_offset, "yptar": yptar_offset},
        "replay_instruction": "Retain the base replay shmsflags and apply these external offsets once; they are not embedded in matrix coefficients.",
        "rcond": rcond,
        "rank": int(rank),
        "fit_terms": len(fit_columns),
        "full_rank": bool(rank == len(fit_columns)),
        "fixed_terms": len(fixed_columns),
        "condition": float(singular[0] / singular[-1]) if singular[-1] else None,
        "singular_values": singular.tolist(),
        "weighting": weight_mode,
        "train": metrics(truth[train], fitted[train]),
        "holdout": metrics(truth[holdout], fitted[holdout]),
        "base_matrix_holdout": metrics(truth[holdout], baseline[holdout]),
        "base_matrix_holdout_definition": "Base coefficients evaluated with the same xtarT input and external replay offsets as this fit.",
        "holdout_by_foil": {str(foil): metrics(truth[holdout & (data["foil"] == foil)],
                                               fitted[holdout & (data["foil"] == foil)])
                            for foil in np.unique(data["foil"][holdout])},
        "residual_columns": ["xptar_slope", "ytar_m", "yptar_slope"],
        "interpretation": "Same-run held-out label-geometry diagnostic; not independent physics validation.",
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result_lines = list(lines)
    for index, power, values in existing:
        if power in fit_terms:
            delta_text = ROW.fullmatch(lines[index].rstrip("\r\n"))[4]
            result_lines[index] = (" " + "".join(f"{v:16.9g}" for v in fit_terms[power])
                                   + f"{delta_text:>16} {power}\n")
    if "00000" in fit_terms and not any(power == "00000" for _, power, _ in existing):
        constant = [*fit_terms["00000"], 0.0]
        line = " " + "".join(f"{v:16.9g}" for v in constant) + " 00000\n"
        first_row = min(index for index, _, _ in existing)
        result_lines.insert(first_row, line)
    header = ("! Generated SHMS SVD from TFit; base header below describes the historical matrix.\n"
              f"! Preserve external pphi_offset/xptar = {xptar_offset:.12g} and yptar offset = {yptar_offset:.12g}; keep replay shmsflags.\n")
    matrix_output = output_dir / "new_matrix.dat"
    matrix_output.write_text(header + "".join(result_lines), encoding="utf-8")
    _, written_rows = read_matrix(matrix_output)
    written = powers(data, written_rows) @ np.stack([values[:3] for _, _, values in written_rows]) + replay_offset
    write_error = np.max(np.abs(written - fitted), axis=0)
    report["written_matrix_max_prediction_delta"] = write_error.tolist()
    if np.any(write_error >= 1e-7):
        raise ValueError(f"matrix text precision changed predictions by {write_error}")
    (output_dir / "fit_report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="ROOT file containing TFit")
    parser.add_argument("--matrix", required=True, type=Path, help="base SHMS matrix")
    parser.add_argument("--out", type=Path, default=Path.cwd())
    parser.add_argument("--rcond", type=float, default=1e-10)
    parser.add_argument("--delta-bin-width", type=float, default=1.0,
                        help="percent units for equal-cell weighting; ignored if fit_weight exists")
    parser.add_argument("--xptar-offset", type=float, default=-8.681269905e-4,
                        help="external replay xptar slope offset, subtracted before matrix fit")
    parser.add_argument("--yptar-offset", type=float, default=0.0,
                        help="external replay yptar slope offset, subtracted before matrix fit")
    args = parser.parse_args()
    report = fit(args.input, args.matrix, args.out, args.rcond, args.delta_bin_width,
                 args.xptar_offset, args.yptar_offset)
    print(json.dumps({key: report[key] for key in ("rank", "fit_terms", "condition", "holdout")}))


if __name__ == "__main__":
    main()
