# SHMS reference delta slices versus the current Run 25521 selection

**The current Run 25521 slices do not match the checked upstream SHMS examples.**
They preserve the customized results-repository edge-based configuration inherited
from Run 25523. They should not be described as the universal or original SHMS
calibration slice definition. No fit, selection or matrix was changed in this check.

## Classic SHMS C macros: centers and half-widths

Both [zwertz/SHMS_OPTICS](https://github.com/zwertz/SHMS_OPTICS/blob/350c7ee59654dbe31a6791b941a317ac2607c0e3/fit_opt_matrix.C#L222)
and [hszumila/shms_optics_a1n](https://github.com/hszumila/shms_optics_a1n/blob/cf7f20a8f838493051c4bd5ebc7c21f983a764fd/fit_opt_matrix.C#L222)
contain the same classic definitions:

    centers:     -11, -8, -4, 0, 4, 8, 17.5
    half-widths:   1,  2,  2, 2, 2, 2,  7.5

The [membership test](https://github.com/zwertz/SHMS_OPTICS/blob/350c7ee59654dbe31a6791b941a317ac2607c0e3/fit_opt_matrix.C#L276)
is center−halfwidth ≤ delta < center+halfwidth. These values are **not consecutive
edges**, even though the center array is named delcut.

| Slice | Classic SHMS interval (%) | Width |
|---|---|---:|
| 0 | [−12,−10) | 2 |
| 1 | [−10,−6) | 4 |
| 2 | [−6,−2) | 4 |
| 3 | [−2,+2) | 4 |
| 4 | [+2,+6) | 4 |
| 5 | [+6,+10) | 4 |
| 6 | [+10,+25) | 15 |

The classic code uses first-accepted chronological event scans and a cap per
foil/delta/y-sieve-column bin. Its MaxPerBin is 200, not our customized 1,000;
its foil cap is 10,000. Those are historical settings, not requirements to impose
on this new handoff. It also has the outer −15<delta<30 gate, but membership in
these particular windows further restricts its accepted range to [−12,+25).

## Run-specific SHMS variants

[zwertz fit_opt_matrix_v2.C](https://github.com/zwertz/SHMS_OPTICS/blob/350c7ee59654dbe31a6791b941a317ac2607c0e3/fit_opt_matrix_v2.C#L254)
reads both centers and half-widths from the run metadata. The
[22045 entry](https://github.com/zwertz/SHMS_OPTICS/blob/350c7ee59654dbe31a6791b941a317ac2607c0e3/DATfiles/list_of_optics_run.dat#L12)
uses:

    centers:     -9, -4, 0, 6, 17.5
    half-widths:  3,  2, 2, 4,  7.5
    intervals: [-12,-6), [-6,-2), [-2,2), [2,10), [10,25)

This is a three-foil +10/0/−10 cm example. It does have an unequal-width first
slice, but **6 percentage points**, not our effective 9. That v2 source sets
MaxPerBin=300 and MaxZtarPerBin=9500. The extra lower boundary at −10 is therefore
not universal across SHMS versions.

The [A1n run-specific metadata](https://github.com/hszumila/shms_optics_a1n/blob/cf7f20a8f838493051c4bd5ebc7c21f983a764fd/list_of_optics_run.dat#L5)
uses finer low-delta windows for runs 10776/10786/10790. Sorted intervals are:

    [-13,-12), [-12,-11), [-11,-10), [-10,-8), [-8,-6),
    [-6,-2), [-2,2), [2,6), [6,10), [10,25)

Their file order places [−13,−12) last; the intervals above are sorted solely
for readability. The A1n v2 fitter uses the same center/half-width membership test.
A final 9611 record in that metadata file is incomplete/inconsistent: declared
count 9, ten subsequent values and no half-width row. It is not a reliable
alternative bin definition. The zwertz test metadata also contains an incomplete
22044 record lacking its documented half-width line; the complete production
22045 entry above is the appropriate example to interpret.

## The separate hszumila/SHMS_optics implementation

[hszumila/SHMS_optics](https://github.com/hszumila/SHMS_optics/blob/c7d70e88b0cf2d1d93359d941168ab8f35ab916e/source/shms_optics.cpp#L743)
is a different calibration implementation: the checked SVD filling loop uses
foil/hole peak cuts and an event count per hole, rather than this C-macro's
foil/delta/y-column bin structure. Its
[Jan19 setup](https://github.com/hszumila/SHMS_optics/blob/c7d70e88b0cf2d1d93359d941168ab8f35ab916e/source/data/setup_optics_Jan19.txt#L1)
sets −12<delta<20 along with a calorimeter cut. The filling loop additionally
has delta-dependent foil cuts and a per-hole count condition. This is useful
historical context, not a drop-in replacement for the user-required current
legacy fitter. No such cuts or numerical-method changes were introduced here.

## Implication for the −6% step

Our current metadata contains **edges** [−25,−6,−2,2,6,10,22] and the current
macro interprets them as consecutive boundaries. Its −15<delta<30 gate creates
effective intervals (−15,−6), [−6,−2), …, [10,22).

Relative to the classic SHMS example, the first two low-delta windows are
collapsed into one broader window and extended downward, and the upper limit
is 22 rather than 25. This is why the current native cap suppresses such a
large fraction below −6%. The [population audit](SELECTION_ORDER_AUDIT.md)
remains valid: that cap creates the main observed step before foil-total balancing.

Unequal delta widths and per-bin caps do appear in upstream SHMS calibration
code, so unequal widths alone do not demonstrate a programming error. However,
the **specific 9%-wide low-delta slice used here is not established by the
checked SHMS examples**. The distinction between preserving the local customized
workflow and reproducing an upstream SHMS calibration selection should have
been explicit earlier.

None of these metadata files contains Run 25521. They establish historical
examples, not a uniquely authoritative binning for this run. A controlled
comparison could use the classic seven-window definition or an explicitly chosen
run-specific definition while retaining the same ROOT normal-equation solver,
fixed coefficients, and recorded-order cap behavior. This source check does not
authorize or silently perform such a refit, nor reinstate historical foil limits.

[Archived source excerpts and configurations](audit/shms_delta_slice_sources.json) ·
[Derived interval checks](shms_delta_slice_comparison.json) ·
[Reproducible source interpretation](reproduce/check_shms_delta_sources.py)
