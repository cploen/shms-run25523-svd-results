# SHMS run 25523 — legacy ROOT SVD results

Results from the supplied single-run student handoff: 433,019 events, one nominal center foil, and 80 occupied sieve holes.

The final fit uses the repository's legacy C++ fitter and ROOT `TDecompSVD` on **Xᵀ W X**, with the student's foil/hole/1%-delta balancing and all events included. There is no held-out sample. ROOT's default cutoff retains **98 of 126 modes** and truncates 28. All three target solves succeed. This is the legacy result, superseding the earlier direct-design Python SVD run.

## Files to open

- **[Fitted SHMS matrix](matrices/nps_shms_newfit_25523_legacy.dat)**
- **[Compatibility changes](LEGACY_COMPATIBILITY_SUMMARY.md)** — every input and fitter adaptation.
- **[Full fit report](REPORT.md)**
- **[Download everything as a ZIP](shms_25523_legacy_root_svd_results.zip)** — open this file and select Download raw.
- **[Old matrix residual summary](plots/fit_opt_matrix_25523_legacy_old_matrix_diff.pdf)**
- **[New matrix residual summary](plots/fit_opt_matrix_25523_legacy_new_matrix_diff.pdf)**
- **[Legacy diagnostics before fitting](plots/old/)** and **[after fitting](plots/new/)** — xptar, yptar, ytar and delta/sieve views.
- [Machine-readable fit report](fit_report.json), [normal-matrix spectrum](normal_matrix_spectrum.tsv), [ROOT QA file](root/fit_opt_matrix_25523_legacy_qa.root).

## Residual RMSE

Unweighted, in-sample comparisons at the same supplied xtarT:

| Quantity | Starting matrix | Legacy ROOT fit |
|---|---:|---:|
| xptar (mrad) | 1.7152 | 1.5604 |
| ytar (mm) | 9.2437 | 0.6234 |
| yptar (mrad) | 3.5324 | 0.9686 |

## xptar convention and replay

No new xptar geometry correction was applied. The supplied targets already include SHMS vertex-to-sieve geometry. Starting-matrix readback matches the stored replay quantities to numerical precision.

Retain external **pphi_offset = -0.0008681269905 rad** exactly once in replay. Delta coefficients and all xtar-dependent matrix rows remain fixed to the supplied starting matrix.

These are fits to supplied weak-label geometric targets, not independent validation or a fresh HCANA replay. All 174,110 review-required events remain included. Installed sieve pose and nominal single-foil geometry are unverified.

## Scope and reproducibility

This repository contains the final results, small handoff/configuration files, and local fitting adaptations under [reproduce/](reproduce/). The large source/derived event trees, split uploads, and intermediate Python-fit results are omitted. The original input ROOT SHA256 is `e08ee264981ad9e571cb7326456d1f26274c91b6b3628d2007f42af76c084b0a`.

Reproduction scripts record this session's absolute `/workspace/shms_run25523` paths; adjust them on another machine. The legacy plotting code comes from `cploen/hallc_spectrometer_angular_optics`, branch `hms-shms-campaign-switch`, commit `21c5d8e439a16e440ecd0307fa20a086d550d143`.
