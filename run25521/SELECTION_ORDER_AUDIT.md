# Recorded-order selection and the −6% delta step

The 1,000-event **native bin cap is the main source of the step**. It is visible
before the additional equal-foil cap, including in foil 1 (z=0), from which the
additional cap removed no events. The fit does not change delta. This is a
selection-population effect, not a discontinuity introduced into delta by fitted
coefficients.

## Direct population evidence

All events in these two neighboring 1%-wide bins pass the initial eligibility
cuts. Counts refer to unweighted events, not sums of supplied weights.

| Population | −7% ≤ delta < −6% | −6% ≤ delta < −5% |
|---|---:|---:|
| All supplied events / eligible | 5,172 | 5,175 |
| After native bin cap | 2,630 | 4,641 |
| After additional foil balancing / fitted | 2,595 | 4,425 |

The handoff population is essentially continuous across this boundary. Native
cap retention is about 50.9% on the lower side versus 89.7% on the upper side.
After foil-total balancing those figures are about 50.2% and 85.5%.

The native bins have delta boundaries [−25,−6,−2,2,6,10,22]%, with the additional
strict delta>−15 gate. The first effective slice spans **9 percentage points**
(−15,−6), while the next spans **4** [−6,−2). Both receive the same 1,000-event
cap for each foil/y-sieve column. Several first-slice bins saturate, suppressing
a larger fraction of the low-delta population. At −6% a new counter begins.
The cap is on delta-by-y-sieve-column bins, not on 1%-delta histogram bins.

For the z=0 foil alone, with no extra foil-total reduction, the corresponding
counts are 1,668 → 865 in [−7,−6) and 1,678 → 1,553 in [−6,−5). This isolates
the native-cap effect from the additional foil balancing.

## Was recorded order preserved?

**Yes.** The source tree's source_full_entry values are strictly increasing.
Preparation scanned rows in that order, kept the first 1,000 eligible events in
each native foil/delta/y-sieve-column bin, and retained the first 24,396 accepted
events per foil. It then wrote their original combined chronological order.
There was no shuffle, delta sorting, resampling, or split-based selection.

An independent single-pass scan applying both native bin caps and the foil-total
cap reproduces **every fitted row index exactly**. The resulting provenance keys
match the balanced ROOT input in order. This confirms the equivalence to a
legacy recorded-order scan with the documented per-foil cap, rather than merely
assuming that a two-stage implementation preserves the same events.

| Foil / z | After native bin caps | Additional foil-total removals | Fitted |
|---|---:|---:|---:|
| 0 / +10 cm | 24,648 | 252 | 24,396 |
| 1 / 0 cm | 24,396 | 0 | 24,396 |
| 2 / −10 cm | 27,710 | 3,314 | 24,396 |

## What can and cannot be concluded about bias

Recorded-order selection does **not** guarantee an unbiased population. The
native bin cap demonstrably changes the delta distribution. The additional
foil-total cap also changes distributions and truncates the late accepted
portion of the +10 and especially −10 cm foils. For the −10 cm foil it removes
34 of 925 native-accepted events in [−7,−6), but 206 of 1,636 in [−6,−5).
Thus its effect is not delta-neutral; in this local comparison it reduces,
rather than creates, the native-cap jump.

If detector/beam conditions drift with event order, first-N selection can also
introduce temporal selection effects; this audit does not establish whether
such drift exists. Neither count comparison alone nor the fact of chronological
selection proves the angular coefficients unbiased. No fitting configuration,
selection, or coefficient was changed for this audit. Any alternative cap or
sampling scheme would be a separate, explicitly agreed fitting comparison.

[Machine-readable checks and counts](selection_order_audit.json) ·
[Reproducible audit script](reproduce/audit_selection_order.py)
