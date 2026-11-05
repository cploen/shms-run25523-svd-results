"""Recompute SHMS target constraints in an existing portable TFit."""

import argparse
import json
from pathlib import Path

import numpy as np
import uproot

HERE = Path(__file__).resolve().parent


def target_values(a, g):
    foil = a['relative_foil_rank']
    col, row = a['relative_hole_col'], a['relative_hole_row']
    if any(str(int(rank)) not in g['foil_z_cm_by_rank'] for rank in np.unique(foil)):
        raise ValueError('Unknown foil rank')
    lo, hi = g['hole_index_bounds']
    if np.any((col<lo)|(col>hi)|(row<lo)|(row>hi)):
        raise ValueError('Hole outside plate')
    for c, r in g['blocked_holes']:
        if np.any((col==c)&(row==r)):
            raise ValueError('Blocked hole labelled as real')
    theta = np.deg2rad(g['theta_deg'])
    zfoil = np.array([g['foil_z_cm_by_rank'][str(int(v))] for v in foil])
    bx, by = a['replay_beam_x'], a['replay_beam_y']
    xv = -by - g['mispoint_x_cm']
    yv = -zfoil*np.sin(theta) + bx*np.cos(theta) - g['mispoint_y_cm']
    zv = zfoil*np.cos(theta) + bx*np.sin(theta)
    xs = g['hole_pitch_cm'][0]*col + g['sieve_center_offset_cm'][0]
    ys = g['hole_pitch_cm'][1]*row + g['sieve_center_offset_cm'][1]
    if g['sieve_type'] == 'shifted':
        ys = ys + g['hole_pitch_cm'][1]/2
    elif g['sieve_type'] != 'centered':
        raise ValueError('Sieve type must be centered or shifted')
    delta = a['reco_dp']
    hb = g['hb_delta_polynomial_cm'][0]*delta + g['hb_delta_polynomial_cm'][1]*delta**2
    distance = g['sieve_z_cm'] - zv
    if not np.all(distance>0):
        raise ValueError('Target behind sieve')
    xp, yp = (xs-xv)/distance, (ys-hb-yv)/distance
    xt, yt = xv-xp*zv, yv-yp*zv
    if not all(np.isfinite(v).all() for v in [xt,yt,xp,yp,hb]):
        raise ValueError('Nonfinite geometry target')
    # Independent forward closure to the labelled hole and beam/foil vertex.
    errors = [np.max(np.abs(xt+xp*g['sieve_z_cm']-xs)),
              np.max(np.abs(yt+yp*g['sieve_z_cm']+hb-ys)),
              np.max(np.abs(xt+xp*zv-xv)), np.max(np.abs(yt+yp*zv-yv))]
    if max(errors)>1e-11:
        raise ValueError('Geometry closure failed')
    return dict(xtarT=xt,ytarT=yt,xptarT=xp,yptarT=yp,ztarT=zfoil,xsT=xs,ysT=ys,
                vertex_x_transport=xv,vertex_y_transport=yv,vertex_z_transport=zv,hb_y_correction_cm=hb), errors


def build(source_path, config_path, output_path):
    source_path, config_path, output_path = map(Path, (source_path, config_path, output_path))
    if source_path.resolve() == output_path.resolve():
        raise ValueError("Source and output must differ")
    temporary = output_path.with_suffix(".tmp.root")
    if output_path.exists() or temporary.exists():
        raise FileExistsError(f"Output exists: {output_path}")
    geometry = json.loads(config_path.read_text(encoding="utf-8"))
    with uproot.open(source_path, handler=uproot.source.file.MemmapSource) as source:
        if "TFit" not in source:
            raise ValueError("Missing TFit tree")
        table = dict(source["TFit"].arrays(library="np"))
    required = ("run", "entry", "label_status", "foil_rank", "hole_col", "hole_row",
                "train", "beam_x_cm", "beam_y_cm", "delta")
    missing = [name for name in required if name not in table]
    if missing:
        raise ValueError(f"Missing TFit branches: {missing}")
    count = len(table["entry"])
    if not count or any(value.ndim != 1 or len(value) != count for value in table.values()):
        raise ValueError("TFit branches must be nonempty equal-length scalars")
    if len(np.unique(table["entry"])) != count:
        raise ValueError("Duplicate entries")
    if not (table["run"] == geometry["run"]).all():
        raise ValueError("Run does not match geometry")
    if not (table["label_status"] == 1).all():
        raise ValueError("Only anchored labels may enter TFit")
    if not np.isin(table["train"], [False, True]).all() or table["train"].all() or not table["train"].any():
        raise ValueError("train must contain both boolean partitions")
    for name, value in table.items():
        if not np.isfinite(value).all():
            raise ValueError(f"Nonfinite source branch: {name}")
    aliases = {"relative_foil_rank": table["foil_rank"], "relative_hole_col": table["hole_col"],
               "relative_hole_row": table["hole_row"], "replay_beam_x": table["beam_x_cm"],
               "replay_beam_y": table["beam_y_cm"], "reco_dp": table["delta"]}
    targets, closure = target_values(aliases, geometry)
    table.update(targets)
    table["xtar"] = targets["xtarT"].copy()
    try:
        with uproot.recreate(temporary) as output:
            output.mktree("TFit", {name: value.dtype for name, value in table.items()})
            output["TFit"].extend(table)
            output["geometry_json"] = json.dumps(geometry, ensure_ascii=False)
        with uproot.open(temporary, handler=uproot.source.file.MemmapSource) as check:
            got = check["TFit"].arrays(library="np")
            if check["TFit"].classname != "TTree" or set(got) != set(table):
                raise AssertionError("Output schema differs")
            if not all(np.array_equal(got[name], value) for name, value in table.items()):
                raise AssertionError("Output readback differs")
        temporary.replace(output_path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return {"events": count, "train": int(table["train"].sum()),
            "diagnostic_holdout": int(np.count_nonzero(table["train"] == 0)),
            "geometry_closure_max_cm": float(max(closure)), "output": str(output_path)}


def selfcheck():
    geometry = json.loads((HERE / "geometry.json").read_text(encoding="utf-8"))
    center_rank = next(int(rank) for rank, z in geometry['foil_z_cm_by_rank'].items() if z == 0)
    event = {"relative_foil_rank": np.array([center_rank]), "relative_hole_col": np.array([0]),
             "relative_hole_row": np.array([0]), "replay_beam_x": np.array([0.]),
             "replay_beam_y": np.array([0.]), "reco_dp": np.array([0.])}
    target, _ = target_values(event, geometry)
    assert np.allclose(target["xtarT"], .126) and np.allclose(target["ytarT"], .06)
    assert np.allclose(target["xptarT"], -.126 / 253)
    assert np.allclose(target["yptarT"], -.06 / 253)
    event["relative_foil_rank"][0] = max(map(int, geometry['foil_z_cm_by_rank'])) + 1
    try:
        target_values(event, geometry)
    except ValueError as error:
        assert "Unknown foil rank" in str(error)
    else:
        raise AssertionError("Unknown foil rank accepted")
    event["relative_foil_rank"][0] = center_rank
    event["relative_hole_col"][0], event["relative_hole_row"][0] = 1, 3
    try:
        target_values(event, geometry)
    except ValueError as error:
        assert "Blocked hole" in str(error)
    else:
        raise AssertionError("Blocked hole accepted")
    return {"selfcheck": "passed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=HERE / "shms_25523_data_0_fit.root")
    parser.add_argument("--geometry", type=Path, default=HERE / "geometry.json")
    parser.add_argument("--out", type=Path, default=HERE / "shms_25523_data_0_fit_adjusted.root")
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    print(json.dumps(selfcheck() if args.selfcheck else build(args.source, args.geometry, args.out), indent=2))


if __name__ == "__main__":
    main()
