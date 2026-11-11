# Run 25521: handoff inspection — fitting blocked on missing inputs

No fit has started. No Run 25523 result or executable fitter has been modified.

The attached `data_1_run25521_adaptive_minimal_20261107.zip` contains only
`data_1.root`, `data_1.npz`, and README.md. The ROOT file has one TTree,
`train`, with 106,058 rows and 41 branches; it has no geometry or target objects.
The ROOT and NPZ have identical fields and values. Both SHA256 values match the
handoff README. All fields are finite and source (run, source_full_entry) keys
are unique. See [machine-readable audit](audit/inspection.json),
[original documentation](audit/HANDOFF_README.md), and
[reproducible inspection script](audit/inspect_handoff.py).

| Foil label | Nominal z (cm), from README | Available | Pass native delta gate only | Fitted |
|---|---:|---:|---:|---:|
| 0 | +10 | 34,429 | 31,401 | 0 |
| 1 | 0 | 33,216 | 31,835 | 0 |
| 2 | -10 | 38,413 | 37,250 | 0 |

The delta-gate column applies only the macro's strict -15 < delta < 30 test.
It is **not** a complete eligibility or balanced-selection count. Sieve targets,
delta slice boundaries and geometry are needed before native delta-by-y-sieve
column bins and their 1,000-event caps can be evaluated. No 15,000/30,000 foil
limit has been imposed. There is no inherited split selection: all historical
split values, including the 482 unassigned rows, remain available.

## Missing inputs requiring resolution before fitting

- No `TFit`, `xtarT`, `ytarT`, `xptarT`, `yptarT`, `ztarT`, `xsT`, or `ysT`
  targets are supplied. This requires target construction, not just renaming a
  tree or converting `ztarT` from integer to Double_t. Foil coordinates alone do
  not specify sieve pitch/pose/distance, angle, pointing, beam conventions,
  index orientation, horizontal-bend corrections, or xptar vertex convention.
- No Run 25521 starting matrix or matrix provenance is included. The repository
  base matrix is a potential historical source, not established by this ZIP as
  the correct matrix for this handoff. Its fixed delta and xtar coefficients
  must not be adopted silently.
- No weight array or weight formula is supplied. `candidate_score` is explicitly
  an indexing diagnostic, not a calibrated probability. The Run 25523 weight
  formula is not evidence of a supplied Run 25521 definition. Weighted fitting
  cannot be labeled “Supplied weights” until a definition is established.
- `reco_xptar_rad` is described as reconstructed radians, but neither the exact
  geometric target slope convention nor external replay slope offsets are
  documented. No additional vertex correction or Run 25523 offset was applied.

FP positions, beam positions and reconstructed target positions are documented
in cm; slopes are documented in radians and delta in percent. The future legacy
adapter must use Double_t branch bindings, cm TFit positions, and divide positions
by 100 for matrix evaluation. The present audit changes no arrays or labels.

## Label and population findings

There are 219 clusters and 209 candidate joint identities. All 106,058 events
have review_required=true and physical_accuracy_verified=false. There are 25,383
direct-window events and 80,675 transferred identities; 9,394 events have identity
competition. The README identifies unresolved column inconsistencies in C038,
C078, C135 and C205. These findings are reported, not used to relabel or discard
rows. The 901 unresolved branch events and 51,081 originally unassigned events
are absent from this package and cannot be recovered by selection changes.

## Execution and validation status

The environment became available and the repository and ZIP were inspected.
NumPy/uproot were used only for inspection, never for fitting. ROOT is not yet
installed; no dependency build or full HCANA build was attempted while required
physics inputs remain unresolved. There are no solver outcomes, matrices, or
fit diagnostics to validate yet. No matrix-parser test, matrix-evaluation test,
or full HCANA replay has been performed for Run 25521.

Once inputs are resolved, both cases must retain the requested legacy C++ ROOT
normal-equation SVD calculation and default truncation, fixed delta/xtar terms,
and the native bin-selection behavior. Full-target slope fitting absorbs a
constant offset; an external offset must not then be applied a second time.
Any weighted target-offset subtraction must instead be documented explicitly.
Future matrix outputs require both literal ` ---` separator lines, a closing
newline, no internal blank lines, and actual-reader validation preserving all
coefficient values. Old/new diagnostics must use matching selected events within
each case, with neutral method labels. None of these pending deliverables is
claimed by this inspection commit.
