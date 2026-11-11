# Data 1 - Run 25521

Adaptive momentum-window indexing snapshot, 2026-11-07.

## Contents

- data_1.root: ROOT tree `train`.
- data_1.npz: NumPy arrays with the same fields and values as the ROOT tree.
- README.md: this documentation.

The main dataset contains 106,058 events in 219 clusters, with 209 distinct candidate joint identities. All momentum values of these cluster members are included; the indexing window is not an event-selection cut on this dataset.

## Indexing method

201 objects use the experimental delta interval 0 to 10 percent. The remaining 18 use the highest available lower window: 5 use -5 to 5 percent and 13 use -10 to 0 percent. The lower windows require at least 20 experimental events and 8 MC reference events. MC momentum windows are converted to the experimental central-momentum convention: delta_common = 100 * ((1 + delta_MC / 100) * 6.358 / 6.332568 - 1). This aligns momentum denominators; MC truth and experimental reconstructed delta remain different estimators.

Matching uses bounded rotation and translation in scaled FP4D. Each object retains its highest-scoring candidate without total-score, score-margin, or coverage acceptance thresholds. Multiple clusters can share an identity and are not merged. This snapshot does not inherit manual overrides from other Data 1 releases.

## Fields and units

- `run`, `source_full_entry`, `source_row`: original event provenance. The source primary key is (run, source_full_entry); source_row is not a ROOT entry number.
- `split`: preserved historical split. 482 main events have split = -1, also indicated by `split_unassigned`; assign an appropriate split before training or testing.
- FP4D: `fp_x_cm`, `fp_y_cm`, `fp_xp_rad`, `fp_yp_rad`.
- Raw6 inputs: FP4D plus `raster_x_adc`, `raster_y_adc` (ADC units).
- `delta_percent`: experimental reconstructed momentum deviation, in percent.
- `z_reco_cm`, `beam_x_cm`, `beam_y_cm`, `reco_xtar_cm`, `reco_ytar_cm`: centimeters. `reco_xptar_rad`, `reco_yptar_rad`: radians.
- `cluster_id`: stable object identifier; `parent_cluster_id` and `is_child_cluster` preserve parent/child relationships. Object identifiers may differ from display labels; an unsplit parent 98 may have object ID 9800.
- `joint_class_id`, `foil_id`, `hole_col`, `hole_row`: candidate identity. Foil 0, 1, 2 correspond to nominal z = +10, 0, -10 cm.
- `index_window_low_percent`, `index_window_high_percent`: selected indexing window.
- `direct_window_mask`: 25,383 events within their object's matching window.
- `identity_transferred`: 80,675 events outside that window inheriting their object's candidate identity. These masks are mutually exclusive and exhaustive in the main dataset.
- `identity_competition`: multiple objects share a candidate identity.
- `index_window_events`, `sparse_window_diagnostic`, `candidate_score`: indexing diagnostics, not calibrated probabilities.
- `review_required`: true for every event.
- `physical_accuracy_verified`: false for every event.
- `original_raw_cluster`, `original_joint_class_id`, `previous_w010_joint`, `previous_m15_joint`: preserved earlier labels for provenance.

## Limitations and population accounting

These are candidate weak labels, not verified physical identities. Direct-window membership does not establish purity. Known column inconsistencies, including C038, C078, C135 and C205, remain subject to review. No new physical validation, manual label correction, training, or event deletion was performed for this package.

Of the original 158,040 valid events, this minimal package contains the 106,058 main events only. The 901 unresolved branch events and 51,081 originally unassigned events remain preserved in the full research release; they are not included in this three-file package.

## Loading

NumPy: `data = numpy.load('data_1.npz', allow_pickle=False)`.
ROOT with uproot: open `data_1.root` and read tree `train`. For large local reads, use `handler=uproot.source.file.MemmapSource`.

## Data file SHA-256

data_1.root: 951cada63c88c60656823837292f6ef1588e25765c82e3f08e2e6d692ae2f168

data_1.npz: b7ffa993c3dc7ac5ea617d8fdd0da45c1df320600ca5af46cd673bd24cd49b37

