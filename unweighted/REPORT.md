# Unweighted legacy X^T X fit

The historical SHMS fitter from commit 3b93f6e is used with only its two foil-total caps lifted to the input-row count. This single-foil dataset is not artificially limited to 15000 events. No weighting function, supplied Python fitter, column rescaling, new numerical method or custom truncation is used.

## Selection and native balancing

Input: 433019 rows; fitted: **50463 rows**. The remaining rows are excluded by the original cuts/bin caps, not by a held-out partition. The original delta-by-y-sieve-column occupancy cap remains **1000 per bin**. There is no delta-only balancing switch. The native cut -15<delta<30 and valid campaign/foil/sieve-bin conditions remain. The overall event limit and both foil-total limits are 433019, so they do not artificially restrict this one-foil sample. Input event order and legacy train/split fields are preserved; those fields do not choose the fit.

The chosen metadata boundaries are [-25,-6,-2,2,6,10,22] percent; the original -15 lower delta cut still applies. The accepted cell counts are recorded in fit_report.json.

## Solve and checks

The fitter forms raw **X^T X**, accumulates the original right-hand sides and calls ROOT TDecompSVD::Solve with the default tolerance. All three solves succeed. The original script does not export a singular spectrum, so the weighted run's retained-mode count is not attributed to this result. All six old/new residual histograms have 50463 entries. All delta coefficients and six xtar-dependent rows are numerically unchanged.

The output is matrices/nps_shms_newfit_25523_unweighted.dat.

Unweighted RMSE on the selected fit events:

| Quantity | Stored starting replay | New matrix |
|---|---:|---:|
| xptar (mrad) | 1.3143 | 1.2253 |
| ytar (mm) | 5.6922 | 0.6202 |
| yptar (mrad) | 2.3377 | 1.0684 |

Over all 433019 input rows, new-matrix RMSE is 1.6646 mrad (xptar), 0.6279 mm (ytar), 1.0099 mrad (yptar). This combines selected and excluded rows; it is not a blind validation sample. The weighted run uses a different selection, so comparisons are not an isolated weighting experiment.

## Output offset convention

The historical macro fits full supplied slopes without subtracting external offsets. Its fitted constant absorbs the slope offset. For **this unweighted output matrix**, use external xptar/pphi_offset=0 and yptar/ptheta_offset=0. Do not additionally apply the starting pphi_offset=-0.0008681269905 rad. This follows from retaining the original target equation and constant fit; no new offset handling was added to the code.

The separate weighted output expects its external xptar offset to remain applied once; do not interchange these replay instructions. Other replay settings remain those supplied with the starting configuration.

## Plots

Old shows the stored starting replay minus the supplied target for the 50463 selected events. New shows the legacy fitted-matrix residuals for those same events. The native plot calculations and histogram ranges are unchanged. A neutral method banner is added to published PDFs; the ROOT QA file retains native canvases.

No supplied geometric target, label, review flag or branch value was changed. This is one run's weak-label geometric fit, not a new HCANA replay, independent label validation, or measurement of multi-foil resolution.

## Full legacy diagnostic suite

The `plots/old/` and `plots/new/` folders now contain matching xptar, yptar and ytar diagnostics, including sieve/delta breakdowns. Both use exactly the 50,463 events admitted by the unweighted fit; accepted cell counts are checked against fit_report.json. The starting matrix is evaluated at supplied xtar/xtarT with its original external xptar offset, and the new unweighted matrix is evaluated at the same inputs with zero external slope offsets. Thus these detailed old/new plots compare matrices on identical inputs. The two automatic summary PDFs retain their original stored-replay-vs-target old residuals, as described above.

Some inherited residual axis titles say target-minus-reconstructed even though the actual fill is reconstructed-minus-target; their source calculations are retained.

All three original plotting macros are unchanged exports from commit 3b93f6e and are available in diagnostics/fit/. The Python helper prepares plotting-only trees and invokes these macros; it does not perform a fit. Neither matrix was changed to add these plots. These remain matrix evaluations, not a new HCANA replay. Neutral method banners are added to every PDF page; ROOT plot files retain native canvases.

Recreate from the original input ROOT file with ROOT, numpy and uproot active:

    python diagnostics/make_unweighted_plots.py /path/to/shms_25523_data_0_fit.root /path/to/temporary_plot_inputs

Then, with PyMuPDF and pypdf installed, add PDF banners:

    python diagnostics/label_plot_pdfs.py unweighted/plots/old unweighted/plots/new --label "UNWEIGHTED LEGACY FIT | 50,463 fitted events | original bin caps | X^T X"
