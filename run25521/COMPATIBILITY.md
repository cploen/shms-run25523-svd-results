# Run 25521 compatibility and provenance

The source ZIP is unchanged. Original audit/checksums are in audit/. User
clarification, after initial inspection: “it is the same as the previous run.
just with more foils.” This authorizes inherited geometry, matrix and weight
formula; it does not authorize inherited event splits, relaxed native bin caps,
or a different solver. The previous weighted path's selection changes and
offset subtraction are deliberately not carried over.

## Inherited definitions and target construction

- Starting matrix: ../../config/base_matrix.dat. Geometry comes from
  ../../config/geometry.json, with foil ranks replaced by 0:+10, 1:0, 2:−10 cm.
  The complete effective geometry is saved in config/geometry.json.
- Target equations are those in `handoff/build_tfit.py:target_values` at results
  repository commit `5f825b5`. Weight formula comes from
  `handoff/run_svd.py:weights` at that same commit. Only its weight definition
  was reused; that Python file's numerical fitting implementation was not run.
- Centered sieve: xs=2.5*hole_col, ys=1.64*hole_row cm, L=253 cm;
  theta=13.505 degrees; x mispoint=−0.126 cm, y mispoint=−0.06 cm.
  Beam coordinates are supplied cm values, with no raw ADC addition.

For each event (all lengths in cm):

    z = foil_z[foil_id]
    xv = -beam_y - mispoint_x
    yv = -z*sin(theta) + beam_x*cos(theta) - mispoint_y
    zv =  z*cos(theta) + beam_x*sin(theta)
    hb = -0.0398*delta + 0.000398*delta^2
    xptarT = (xs - xv)/(L - zv)
    yptarT = (ys - hb - yv)/(L - zv)
    xtarT = xv - xptarT*zv
    ytarT = yv - yptarT*zv

These slopes connect the transport-frame vertex to the sieve, then positions
are projected back to z=0. The xptar numerator already includes the beam and
mispoint vertex correction. No later correction is added. Forward closure to
both labelled holes and vertices is checked below 1e−11 cm.

The generic spectrometer_profiles.def still declares yMP=−0.05 cm, whereas the
previous supplied handoff geometry explicitly uses −0.06 cm. We preserve the
**handoff value −0.06** for target construction. The fitter and diagnostic macros
do not call targetTruth or use the generic yMP to construct/alter these supplied
TFit targets. Generic profile TNamed metadata in ROOT outputs is therefore not
the authoritative run geometry; use config/geometry.json. No silent 0.01 cm
change to the inherited target definition was made.

## ROOT adapter

This package has a `train` TTree with 41 branches, not TFit. The adapter keeps all
41 original arrays and adds aliases and geometric quantities in a derived TFit.
The complete derived copy preserves all 106,058 rows, original types and order;
the balanced copy preserves original values/types on the selected subsequence.
Both are read back and checked. Original fields are never overwritten.

| Added branch | Definition |
|---|---|
| xfp, yfp, xpfp, ypfp | fp_x_cm, fp_y_cm, fp_xp_rad, fp_yp_rad |
| delta, ztar | delta_percent, z_reco_cm |
| xptar, yptar, ytar | reco_xptar_rad, reco_yptar_rad, reco_ytar_cm |
| xtar, xtarT | geometric xtarT; original reco_xtar_cm remains separate |
| xptarT, yptarT, ytarT, ztarT | geometry above; ztarT is newly created Double_t |
| xsT, ysT | unchanged hole labels × inherited sieve pitch |
| xs, ys | stored reconstruction projected to sieve, including hb in ys |
| vertex_*_transport, hb_y_correction_cm | intermediate quantities above |
| fit_weight (balanced tree) | previous occupancy formula on selected events |

Unlike the previous handoff, there is no original integer ztarT to convert.
All added fitter/diagnostic aliases and targets are float64/Double_t. Neither
the TTree name `train` nor historical `split` values cause partition selection.
Original source_row is never used as a ROOT entry number. Event provenance is
(run, source_full_entry), retained verbatim.

## Fitter adaptation

[Run-specific source](reproduce/fit_run25521.C) is generated from the unchanged
repository legacy macro by [adapt_fitter.py](reproduce/adapt_fitter.py). The
[complete diff](reproduce/legacy_changes.diff) records:

1. Function/include-path and explicit standalone compilation includes.
2. Optional reading of positive finite fit_weight, multiplication of both
   normal-matrix and right-hand-side contributions by that weight once.
   In unweighted mode every weight is exactly 1.
3. Logging the native default tolerance/spectrum/solve statuses and saving
   accumulated normal matrix and native solutions for verification.
4. Adding the already-computed fixed xtar contribution to the xptar distribution
   histogram. Residual reconstruction already included it; solver unchanged.

The existing input-count-based foil caps, native 1,000-event bin cap, delta gate,
basis, row order and TDecompSVD call are unchanged. Population balancing happens
in input preparation as documented in README. No external slope offset is
subtracted in either case, so both output matrices require zero external slope
offsets. Unlike the older Run 25523 weighted matrix, the new weighted matrix
must **not** have the starting offset applied in replay.

## Legacy diagnostics and limitations

The existing three plotting macros run unchanged for all four case/old-new
combinations, on the exact fitted events. They display event-count residuals,
not fit-weighted histograms. Matrix evaluation uses identical geometric xtar
for old/new; starting slopes receive the independently verified starting offset
once and both new matrices receive zero external offset. Positions convert from
cm to metres for evaluation and back to cm for legacy plotting.

Two historical ytar views have embedded display shifts: the ytar-versus-yptar
2D histogram fills ytar−ytarT−0.035 cm, and the ytar delta-profile histogram fills
ytar−ytarT+0.035 cm. Sieve-column ytar residuals use ytar−ytarT with no shift.
These plotting conventions are retained in both old/new suites, not added to
fit targets, coefficients or reported numerical RMSE. Some inherited xptar
axis titles say “true − reconstructed” although the macro fills reconstructed
minus target. Numerical JSON residuals consistently use reconstructed minus
target. Delta legends use nominal bin midpoints; the first midpoint −15.5%
includes only events above the native −15% gate.

No new physical label verification, foil survey, full HCANA replay, iterative
extended-target reconstruction, momentum fit or cross-run validation is claimed.
Old automatic summary and full old diagnostics differ in xtar convention as
explained in README; all are based on matching selected events. Empty or sparse
legacy bins remain visible rather than prompting label changes.
