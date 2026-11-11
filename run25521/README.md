# Run 25521: foil-balanced legacy ROOT SVD results

Both fits are complete. They use **73,188 identical events, 24,396 per foil**,
with no inherited split selection or held-out sample. Run 25523 results are unchanged.
User clarification authorizes the previous run's geometry, starting matrix,
weight definition and conventions, with the three foil positions from this ZIP.

**[Requested NPS_HMS_OPTICS legacy macros: per-foil old/new reports](NPS_LEGACY_DIAGNOSTICS.md).**

**Before/after delta versus ytar:**
[Unweighted PDF](unweighted/plots/comparison/25521_delta_vs_ytar_before_after.pdf) ·
[Supplied weights PDF](weighted/plots/comparison/25521_delta_vs_ytar_before_after.pdf).
Left = starting matrix; right = new fit. Page 1 combines foils; pages 2–4 show
+10, 0, and −10 cm foils separately. Both use identical events, bins, axes and
a single shared logarithmic event-count color scale. Ytar is evaluated at the
same geometric xtar before and after; this is a matrix comparison, not a full replay.
All events are inside the plotted ranges.

New-fit **delta versus ytar**, with all-foil and separate-foil panels:
[Unweighted PDF](unweighted/plots/new/25521_new_delta_vs_ytar.pdf) ·
[Supplied weights PDF](weighted/plots/new/25521_new_delta_vs_ytar.pdf).
Horizontal axis: fitted ytar (cm); vertical axis: delta (%). Colors are event counts
on a shared logarithmic scale. All 73,188 selected events are shown without clipping.


**[Supplemental distributions for each foil and delta slice](DIAGNOSTICS.md).**
Each foil has separate old/new reports, with direct links to all six delta slices,
residual distributions by sieve column, and sieve/delta views. These expanded
displays supplement the original legacy PDFs linked below.

| Deliverable | Supplied weights | Unweighted legacy fit |
|---|---|---|
| Replay matrix | [Matrix](weighted/matrices/nps_shms_newfit_25521_weighted.dat) | [Matrix](unweighted/matrices/nps_shms_newfit_25521_unweighted.dat) |
| Automatic old summary | [PDF](weighted/plots/fit_opt_matrix_25521_weighted_old_matrix_diff.pdf) | [PDF](unweighted/plots/fit_opt_matrix_25521_unweighted_old_matrix_diff.pdf) |
| Automatic new summary | [PDF](weighted/plots/fit_opt_matrix_25521_weighted_new_matrix_diff.pdf) | [PDF](unweighted/plots/fit_opt_matrix_25521_unweighted_new_matrix_diff.pdf) |
| Full old diagnostics | [Folder](weighted/plots/old/) | [Folder](unweighted/plots/old/) |
| Full new diagnostics | [Folder](weighted/plots/new/) | [Folder](unweighted/plots/new/) |
| Numerical report | [JSON](weighted/fit_report.json) | [JSON](unweighted/fit_report.json) |
| Solver outcome | [JSON](weighted/solver.json) | [JSON](unweighted/solver.json) |

The original suite in each case has two automatic summary PDFs plus seven legacy PDFs under each of
plots/old and plots/new: xptar, yptar and ytar residuals; each axis by sieve; and
ytar versus delta. Xptar residual pages cover all 3 foils × 6 delta slices.
That original suite has 16 PDFs / 70 pages per case. Every page carries its neutral method label.
The legacy plot histograms are event-count diagnostics, without fit weights;
weighted RMSE is separately reported in the JSON.

## Available, eligible and fitted populations

| Foil label | Nominal z (cm) | Available | Eligible before cap | After native bin cap | Fitted in each case |
|---|---:|---:|---:|---:|---:|
| 0 | +10 | 34,429 | 31,312 | 24,648 | 24,396 |
| 1 | 0 | 33,216 | 31,667 | 24,396 | 24,396 |
| 2 | −10 | 38,413 | 37,030 | 27,710 | 24,396 |

Eligibility preserves the macro's abs(delta)<100 outer guard, strict
−15<delta<30 gate, valid foil and y-sieve-column lookup, and the previous run's
delta boundaries [-25,−6,−2,2,6,10,22] percent. Thus the effective interval here
is −15<delta<22. The native first-1,000-events-per-foil/delta/y-sieve-column cap
is evaluated in original source order. Equal foil counts then use the smallest
remaining population, **24,396**, retaining the first that many accepted events
per foil and their original relative order. The C++ fitter rechecks its unchanged
native gates/caps and accepts every prepared row; its logs confirm all counts.
There is no delta-only switch and no historical 15,000/30,000 foil limit.

Selections are identical between cases. Balancing removes 252 accepted events
from +10 cm and 3,314 from −10 cm; this is the consequence of equal foil counts,
not an arbitrary historical limit. All original split values, including −1,
participate before these physics/native-selection rules. The audit and
[selection report](selection.json) retain the complete population accounting.

## Weights and solver

The ZIP has no weights. Following the user's clarification, the previous run's
supplied formula is reused, with populations recomputed on the actual 73,188
fitted events:

    cell = (foil_id, hole_col, hole_row, floor(delta_percent / 1))
    w_i = (1 / count(cell_i)) / mean(1 / count(cell_i))

Each occupied foil/hole/1%-delta cell has equal total weight; mean event weight
is one. These are occupancy-balancing weights, not candidate-score, purity,
measurement-error, or inverse-variance weights. Equal event counts per foil do
not imply equal weight sums: there are 1,854 / 1,964 / 2,125 occupied cells, giving
foil weight sums 22,831.996 / 24,186.645 / 26,169.359. No extra foil-weight scaling
was added, since that would change the supplied formula.

The run-specific C++ copy forms unweighted XᵀX or weighted XᵀWX and matching
right-hand sides, with weights applied once. ROOT TDecompSVD uses its default
truncation; there is no normalization of columns, regularization, direct-design
least-squares solve, or custom cutoff. All three target solves succeed.

| Case | Fit terms | Retained / truncated | ROOT tolerance | Normal-matrix cutoff |
|---|---:|---:|---:|---:|
| Unweighted legacy fit | 126 | 94 / 32 | 2.2204460492503131e−16 | 1.6268028001233974e−11 |
| Supplied weights | 126 | 95 / 31 | 2.2204460492503131e−16 | 1.6265323117244652e−11 |

Singular spectra and the accumulated normal matrices/native solutions are saved
in each case. Only xtar-independent xptar, ytar and yptar coefficients, including
the constant, are fitted. All original delta coefficients and all six
xtar-dependent rows are numerically preserved; constant delta is zero.

## Residual comparison

RMSE on the identical selected population, in **mrad / mm / mrad** for
xptar / ytar / yptar, evaluated at the same geometric xtar:

| Matrix | Event-count RMSE | Supplied-weight RMSE |
|---|---|---|
| Starting | 2.557 / 6.545 / 2.272 | 2.267 / 5.999 / 2.203 |
| Unweighted legacy fit | 2.021 / 4.319 / 1.513 | 1.978 / 4.070 / 1.439 |
| Supplied weights | 2.087 / 4.392 / 1.519 | 1.871 / 3.959 / 1.430 |

These are in-sample residuals against candidate geometry labels, not independent
physical validation. Non-Gaussian tails and outer-sieve xptar structure remain.
The attached README explicitly flags known column inconsistencies.

## Geometry, compatibility and replay instructions

See [compatibility details](COMPATIBILITY.md). Positions remain cm in TFit and
metres in matrix evaluation; slopes are dimensionless and delta is percent.
Target construction uses the previous handoff's vertex-to-sieve equations once,
with z=+10/0/−10 cm and unchanged hole labels. No second vertex correction is
added. The original reconstructed xptar field is retained separately.

The starting matrix evaluated at this handoff's stored reconstructed xtar
reproduces all stored xptar/ytar/yptar values after applying **−0.0008681269905 rad
to xptar, zero to yptar**, with maximum discrepancy below 4.1e−16 in slope/metres.
This confirms the convention from this dataset rather than blindly copying it.

**Both NEW matrices fit full target slopes and require zero external xptar and
yptar offsets.** Their constants absorb the offset. Disable the old
−0.0008681269905 xptar/pphi offset when using either new matrix. Neither weighted
nor unweighted path subtracts that offset before fitting. Retain the authorized
previous momentum/replay settings and fixed delta coefficients; no delta or
central-momentum recalibration was performed. Old diagnostic matrix evaluation
uses the confirmed starting offset once.

Automatic old summaries use the stored starting-replay reconstruction on the
selected events; automatic new summaries use the native unrounded fitted
solutions with fixed terms. The full old/new diagnostics instead evaluate both
emitted matrix files at the same geometric xtar inputs. Thus each comparison
uses matching events, but the old summary and full old diagnostic values can
differ slightly due to the xtar input. Output matrices retain the historical
nine-significant-digit writer precision.

## Inspection findings and validation

The initial [audit](audit/inspection.json) records the pre-clarification state:
no fit had started and geometry/weights were absent from the ZIP. The user's
subsequent clarification resolved those missing definitions; this README records
the completed state. The original [handoff README](audit/HANDOFF_README.md) is
preserved as documentation, not as permission to override the user's requirements.

ROOT and NPZ have exactly matching 41 fields and 106,058 rows; both checksums
match, all values are finite, and provenance keys are unique. There are 219
clusters, 209 candidate identities, 80,675 transferred identities, and 9,394
events with identity competition. All events require review and none is marked
physically verified. Neither nominally blocked hole occurs. The absent 901
branch and 51,081 unassigned events cannot be recovered from this package.
Labels were neither corrected nor filtered by review/indexing flags.

[Validation evidence](validation.json) checks native solution/output values,
fixed coefficients, independent sums of normal-matrix elements, selected-event
counts in every old/new axis, all PDF pages and method labels, and delimiters.
The [actual HCANA reader harness](replay_format_validation.json) loaded all 132
rows of both new matrices with exact coefficients/exponents; malformed-file
negative controls were rejected. Both separators have literal prefix ` ---`,
there are no internal blank lines, and the closing newline is preserved.
No post-fit formatting repair changed any coefficient.

These are parser and matrix-evaluation checks, **not a full HCANA replay**.
No HCANA build was needed. ROOT 6.40.00 was installed in a task-local Python
virtual environment; exact dependency versions and reproduction scripts are in
[reproduce/](reproduce/). Compiled binaries and large derived event trees are
excluded; they are reproducible from the supplied ZIP.
