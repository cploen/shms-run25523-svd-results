# SHMS 25523: legacy ROOT normal-equation SVD

This result supersedes the earlier Python direct-design SVD result for the user's requested legacy fitting method. It runs the repository fit_opt_matrix_gmm.C from hms-shms-campaign-switch (21c5d8e439a16e440ecd0307fa20a086d550d143), with the transparent local input/weight/offset adaptations in legacy_fitter_changes.diff. Repository files were not modified.

## Actual solver

The original C++ loop accumulates the unscaled normal matrix and right-hand sides:

    A = X^T W X
    b = X^T W (target - fixed_xtar_terms - external_offset)
    TDecompSVD decomposition(A)
    decomposition.Solve(b)

Equivalently, apply sqrt(W) to each row of X and target first, then solve on X_weighted^T X_weighted. There is no column normalization, no direct-design least-squares solve, no added regularization, and no custom singular-value tolerance. ROOT's default truncation is allowed.

- Events fitted: 433,019; no held-out events.
- Polynomial terms: 126; normal-matrix singular values retained: 98; truncated: 28.
- ROOT default tolerance: 2.2204460492503131e-16; absolute singular-value cutoff: 9.6279743428074216e-11.
- ROOT returned success for all three target solves. See root_legacy.log and normal_matrix_spectrum.tsv.
- Student's balancing preserved: equal total weight for each occupied foil/hole/1%-delta cell, computed over all supplied events. One nominal z=0 foil is present.
- The derived input converts the integer-valued ztarT branch to Double_t, retaining the exact zero foil coordinate, because the legacy ROOT reader requires that type. The original ROOT file is unchanged.
- Original legacy event caps/per-hole quotas were removed so they do not override the requested all-event fit and the student's supplied weighting.
- Targets, weak labels and review flags are unchanged. All 174,110 review_required events remain included. All supplied deltas, including the 128,734 events below -10%, are included. No additional acceptance cut was applied.

## Result

The fitted matrix is matrices/nps_shms_newfit_25523_legacy.dat. Every delta coefficient and all six xtar-dependent rows remain numerically equal to the starting matrix. Only xtar-independent xptar/ytar/yptar coefficients, including a constant, are fitted.

Unweighted in-sample RMSE, comparing both matrices at the same supplied xtarT:

| Quantity | Starting matrix | Legacy ROOT fitted matrix |
|---|---:|---:|
| xptar (mrad) | 1.7152 | 1.5604 |
| ytar (mm) | 9.2437 | 0.6234 |
| yptar (mrad) | 3.5324 | 0.9686 |

fit_report.json includes weighted residuals, original-replay comparisons and the exact ROOT tolerance. The earlier Python result used column scaling and a direct-design SVD, so its rank and predictions need not match this normal-equation result.

## xptar convention

No new xptar geometry correction was made. The supplied targets already use the SHMS vertex-to-sieve ray, satisfying xsT=xtarT+253*xptarT. Their exact recomputation and the starting matrix's agreement with stored replay values were verified in the previous audit (included as handoff_audit.json). The HCANA-compatible slope sign, units, coefficient ordering and external offset are retained. The nominal geometric assumptions are not independently validated.

Retain pphi_offset=-0.0008681269905 rad exactly once when replaying this output matrix. The fitter subtracts this offset from the xptar fit target and adds it back for reconstructed residuals; it does not embed it in the fitted coefficients. Retain the other supplied replay settings. No actual HCANA replay was executed.

## Diagnostic plots

The two fit_opt_matrix_25523_legacy_*_matrix_diff.pdf files and ROOT QA output are produced by the legacy C++ fitter itself. Its old plots use the original stored replay values; its new plots use the fitted coefficients plus fixed terms and external offsets. Each residual histogram contains all 433,019 events. Gaussian fits use the original histogram ranges.

Fourteen further PDFs in plots/old and plots/new come from the repository's unmodified SHMS-capable legacy xptar/yptar/ytar plotting macros, evaluated from the emitted text coefficients at the supplied xtarT. Here old and new use identical inputs, allowing a matrix-to-matrix comparison. These are not fresh iterative replay trees. Plot-only delta boundaries extend the first interval to include the supplied low-delta tail; the existing histogram ranges are retained. Some legacy axis titles say true-minus-reconstructed, but their fill expressions are reconstructed-minus-true.

## Reproduce

prepare_root_legacy.py creates the derived fit tree, adding the student's per-event fit weights without changing source branches, and produces the adapted macro. The original macro, adapted source, full diff, execution log, and original SHMS plotting code are included. With ROOT/PyROOT, numpy and uproot available in this workspace:

    source /workspace/.optics/activate.sh
    python /workspace/shms_run25523/prepare_root_legacy.py
    bash /workspace/shms_run25523/run_root_legacy.sh

The script uses the existing prepared handoff under /workspace/shms_run25523/handoff. Large input and derived ROOT trees are omitted from the compact result archive. Adjust paths when using a different machine.

This verifies a numerical legacy fit to one run's weak labels. It does not establish independent label accuracy, installed target/sieve geometry, cross-run performance or multi-foil vertex resolution.
