# Data 0 v0.1.0: SHMS Run 25523 SVD handoff

This package converts the unchanged **433,019-event Data 0 v0.1.0 sample** into a standard ROOT `TFit` TTree for nominal SHMS optical-matrix fitting. All **80 cluster IDs**, original hole assignments, all **24 original fields and their dtypes**, review flags, and inherited data partitions are retained. No events are subsampled or reassigned.

The assigned holes remain weak labels. The **174,110 `review_required` events remain included**, with their flags intact. `*T` branches are geometry-derived constraints, not independent measurements of physical truth.

## Files

| File | Purpose |
|---|---|
| `shms_25523_data_0_fit.root` | `TFit`: 433,019 events, 57 scalar branches; includes all original Data 0 fields, conventional SVD branches, full-replay event mapping, and embedded `geometry_json`. |
| `geometry.json` | Run 25523 nominal single-carbon-foil geometry, units, replay offsets, assumptions and evidence. |
| `schema.json` | Names, dtypes, units, provenance and meaning of every branch. |
| `base_matrix.dat` | Starting SHMS matrix, checked numerically against this run's original replay. |
| `build_tfit.py` | Recompute geometric targets after editing geometry; refuses to overwrite existing output. |
| `run_svd.py` | NumPy SVD fitter; no native ROOT or clustering software required. |
| `svd_result/` | Reference fit and numerical report for the supplied, unchanged data and geometry. |
| `manifest.json` | Input identities/hashes, exact skim-to-full replay mapping checks, source version and partition counts. |
| `validation.json` | Event/field preservation, portable rebuild and SVD execution checks; physical accuracy remains unverified. |
| `SHA256SUMS.txt` | Integrity hashes for every other delivered file. |

## Fit

Python with `numpy` and `uproot` is sufficient. From the unzipped package directory:

```sh
python run_svd.py --input shms_25523_data_0_fit.root --matrix base_matrix.dat --out refit
```

The output is `refit/new_matrix.dat` and `refit/fit_report.json`. The fit updates xtar-independent **xptar / ytar / yptar** coefficients plus a constant. All delta coefficients and xtar-dependent coefficients remain fixed. Occupied foil/hole/1%-delta cells receive equal total fit weight.

`train = (legacy_split == 0)` gives **260,173 fit events**. The other **172,846 events** form the same-run diagnostic holdout: CAL 43,050; VAL 43,217; TEST 86,579. Their original `legacy_split` values remain available. Selection/weak-label construction used this run; these partitions do not constitute independent blind validation.

The original HMS C++ fitting macro needs SHMS-specific run lists, matrix/cut settings and event-limit adaptations. The supplied Python runner is the tested execution path.

## Change geometry

Edit `geometry.json`, then run:

```sh
python build_tfit.py --selfcheck
python build_tfit.py
python run_svd.py --input shms_25523_data_0_fit_adjusted.root --matrix base_matrix.dat --out refit_adjusted
```

The rebuild keeps the original events, labels, quality flags, measured/replay observables and partition. Reference results apply only to the original supplied geometry. `run_svd.py` does not read `geometry.json`; if the external slope offsets change, pass matching `--xptar-offset` and `--yptar-offset` values to the fitter and replay. The selfcheck tests the supplied nominal configuration.

## Conventions that must travel with the data

- **Event identity:** `(run, entry)` remains the original Data 0 key. `entry` is the zero-based row in the **979,508-event source skim T**, not the full replay row or DAQ event number. `source_row` still refers to the frozen 531,390-event selected sample. The additional `source_full_entry` identifies the exactly matched row in the full **2,051,311-event replay T**. Never interchange these namespaces.
- **Units:** TFit positions are cm, slopes are dimensionless (conventionally expressed in rad), and delta is percent. The fitter converts positions to metres once. The original Data 0 float32 focal-plane fields remain exact; the conventional `xfp/xpfp/yfp/ypfp` aliases use matching full-precision replay values.
- **Beam:** `beam_x_cm/beam_y_cm` come from the matched full replay `P.rb.x/P.rb.y`; raw raster ADC is preserved separately and is not a position in cm. Replay beam positions already contain BPM/raster contributions. Do not add raster again. No new beam calibration is performed.
- **Single foil:** `foil_rank=0` means the nominal C foil at **z=0 cm**. This is not the old Run 25521 three-foil ranking. The z coordinate comes from the Run 25523 MC's nominal center-foil assumption; it is not a surveyed foil position.
- **Sieve:** pitch 2.50/1.64 cm and blocked-hole pattern `(1,3),(-1,-1)` follow the project-confirmed plate pattern. Centered grid, zero plate offsets and 253 cm sieve distance are nominal modeling constraints. The installed plate type/pose for Run 25523 is unverified. Effective replay/runlist angle 13.505 degrees is used here; the inherited MC input angle 13.495 degrees is separately recorded.
- **Targets:** `xptarT/ytarT/yptarT/xtarT` are generated from the assigned holes, nominal geometry and inherited replay beam with the SHMS HB/delta correction. Ordinary reconstructed target/sieve branches remain diagnostics. `xtar` follows the fit constraint `xtarT`; the old reconstruction is retained as `xtar_replay`.
- **Label status:** `label_status=1` means a retained Data 0 weak-label nominal-fit candidate in this package. It does not assert independent anchoring or physical truth. Original `cluster_id/hole_col/hole_row`, membership strength and all four quality flags remain unchanged.
- **Replay offsets:** retain `pphi_offset=-8.681269905e-4`, `ptheta_offset=0`, `pdelta_offset=0`, and `ppcentral_offset=-0.4`. The fitter handles external slope offsets separately; apply them once. Nominal signed momentum is -6.358 GeV/c; the replay magnitude is 6.332568 GeV/c.

## Provenance and validation boundary

Source release: `outputs/data_0_run25523_v0_1_20261026`. The source skim is `RootData/single_foil_20260928/skimmed_shms_coin_replay_production_25523_-1.root`; the full original replay is `RootData/shms_coin_replay_production_25523_-1.root`. Their identities, exact event mapping, checked columns and numerical replay readback are recorded in `manifest.json`. Full replay and clustering inputs are not needed to run the delivered fitter or geometry rebuild.

Project rebuild entry point: `experiments/data_0_svd_handoff_20261026/build_handoff.py`; the mapping probe and independent checks are archived alongside it. The original Data 0 release and prior Run 25521 packages are preserved.

Hashes, exact event alignment, geometry closure, same-run residuals and a successful SVD establish packaging/reproducibility evidence. They do not establish independent physical accuracy or cross-run validity. Confirm the installed target/sieve geometry and validate a separate replay configuration before using a fitted matrix for production physics.
