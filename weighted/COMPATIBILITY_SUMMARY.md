# Run 25523 handoff: changes for the legacy ROOT SVD fitter

The supplied original `shms_25523_data_0_fit.root` was left unchanged. The fit used a derived copy, `SHMS_legacy_25523/trees/Optics_25523_-1_fit_tree_gmm.root`. The starting point for the fitter was `fit_opt_matrix_gmm.C` from repository branch `hms-shms-campaign-switch`, commit `21c5d8e439a16e440ecd0307fa20a086d550d143`.

## Changes to the ROOT input

| Change | Reason | Effect on data |
|---|---|---|
| Convert `ztarT` from `int64` (`Long64_t`) to `float64` (`Double_t`). | The legacy macro binds this branch to a `Double_t*`. ROOT rejected the integer branch with a `SetBranchAddress` type mismatch. | All foil coordinates remain exactly 0 cm. This was the only dtype conversion. |
| Add a `Double_t` branch named `fit_weight`. | Carry the supplied balancing into the C++ fitter. These weights were calculated by the supplied Python `weights()` function; they were not already stored in this handoff tree. | No event or label changes. Each occupied foil/hole/1%-delta cell receives equal total weight. Weights were recalculated over all events, as requested, instead of only the supplied training partition. |
| Write the derived file as `Optics_25523_-1_fit_tree_gmm.root`. | Match the legacy fitter's existing filename lookup for optics ID 25523 and FileID -1. | Naming/layout only. The tree was already named `TFit`, and its existing conventional branch names were usable without renaming. |

The derived file retains all 57 original branches and adds only `fit_weight`. A direct comparison verified identical values and ordering in every original branch for all **433,019 events**. Every original dtype is unchanged except `ztarT`. The supplied geometry JSON was copied into the derived file.

There was no relabeling, clustering, event duplication, removal, unit conversion in the stored branches, or recomputation of xptarT/ytarT/yptarT/xtarT. The supplied `xtar` input, already equal to their geometric `xtarT`, was retained; it was not replaced with `xtar_replay`. All partition and review flags were preserved, including the 174,110 `review_required` events.

## Campaign files needed by the legacy interface

These are external configuration files, not changes to the supplied ROOT tree:

- A minimal rungroup TSV mapping `run25523` to optics ID `25523`.
- An optics metadata entry using the supplied nominal geometry: angle **13.505 degrees**, **one foil at z=0 cm**, and **centered sieve** (`SieveFlag=1`). This records the handoff assumptions; it does not establish a new survey or plate identification.
- Delta boundaries `[-25,-6,-2,2,6,10,22]` percent, covering the supplied range of approximately **-24.8873% to +21.9963%**. These satisfy the legacy bin bookkeeping. They do not define the supplied 1%-delta weighting cells, which are computed separately by their original weighting function.
- An input path containing the campaign component `SHMS_legacy_25523`, so the repository's existing spectrometer selector chooses SHMS rather than HMS.

## Changes to the fitter's behavior

These go beyond ROOT-file compatibility and are included explicitly for transparency:

1. **Read and apply the supplied weights.** Add `SetBranchAddress("fit_weight", ...)`, multiply both the normal matrix and right-hand sides by each event's weight, and solve:

       A = X^T W X
       b = X^T W (target - fixed_xtar_terms - external_offset)

   This is the legacy normal-equation method applied to weighted rows. The original C++ macro did not consume these weights.

2. **Use all supplied events.** Set the overall event limit to 433,019; remove the original 1,000-event bin, 15,000-event foil, and 30,000-event run/foil caps from the acceptance condition. Replace the hard-coded `-15 < delta < 30` condition with a finite-delta check, while retaining the outer `abs(delta)<100` guard and valid foil/delta/sieve-bin bookkeeping. All supplied events pass the remaining checks. This preserves the supplied supplied sample, including its low-delta tail; it is not a requirement for merely opening the file. The existing `train` and `legacy_split` fields are not used to hold out events.

3. **Handle the existing external slope offset explicitly.** Subtract the supplied `pphi_offset = -0.0008681269905` rad from the xptar target before solving, then add it back when evaluating reconstructed residuals. The yptar offset is 0. The fitted matrix therefore expects the same external xptar offset to be applied once in replay. This changes offset handling in the legacy macro, not the supplied xptar target geometry or the offset's value.

4. **Make the diagnostic reconstruction complete.** Include fixed xtar-dependent terms and the external offset in the new xptar distribution; include the external offsets in the new residuals. Add the offset instruction to the output matrix header.

5. **Record the native solver outcome.** Write singular values, ROOT's default tolerance/cutoff, retained-mode count, and event count. These additions do not change the solve.

6. **Build/run the local copy.** Rename its function/file to `fit_opt_matrix_gmm_legacy`, adjust the helper-header path, and add explicit `<cmath>`, `<TF1.h>` and `std` namespace declarations for standalone ACLiC compilation. The tracked repository source was not edited.

## What remained the legacy calculation

The C++ macro still forms the unscaled normal matrix and uses ROOT `TDecompSVD::Solve`. No column rescaling, direct-design NumPy solve, custom SVD cutoff, or rank rescue was introduced in this result. ROOT's default tolerance was `2.220446049250313e-16`; it retained **98 of 126 modes** and truncated **28**. All three solves succeeded.

The starting matrix's delta coefficients and all six xtar-dependent rows were preserved numerically. Only xtar-independent xptar, ytar, and yptar terms, including a constant, were fitted. No new xptar vertex correction was made: the supplied targets already included the SHMS vertex-to-sieve expression.

## Verification and files

- Original ROOT file SHA256 matched the supplied handoff checksum.
- All 57 original branch arrays match the derived copy exactly in value and order; only `ztarT` changes dtype.
- The final legacy run reads and fits all 433,019 events with no branch-type errors.
- All three solves succeed, output fixed coefficients are preserved, and each of the six old/new residual histograms records 433,019 entries.

The earlier implementation and full diff remain in prior Git history. Adapted executable fitters are omitted from the current repository; the only current fitter is the separate, unchanged original used for unweighted/. The retained execution log is run.log.
