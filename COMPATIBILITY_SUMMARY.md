# ROOT input compatibility

For the unweighted original fitter, the only branch change was `ztarT`: int64/Long64_t became float64/Double_t, preserving the exact zero foil coordinate. A derived copy was named `Optics_25523_-1_fit_tree_gmm.root` to match the original filename lookup. The tree was already named TFit, and all other branch names and dtypes were accepted as supplied.

All 57 original branch values and all 433,019 rows were verified unchanged, including labels, geometric targets, xtar, legacy partitions and review flags. No weights were added to this derived copy. The original input file was untouched. `prepare_input.py` only performs this copy/type conversion and readback check; it is not a fitter.

Minimal campaign metadata selects SHMS, optics ID 25523, 13.505 degrees, one nominal z=0 cm foil, and centered sieve. The delta boundaries are [-25,-6,-2,2,6,10,22] percent. The original script's delta cut and native bin cap still apply. No balancing function was added. The two foil-total caps were lifted to the input count for this single-foil run; the original 1000-event delta-by-sieve-column cap and numerical solver remain unchanged.

The separate earlier weighted run required additional fitter changes. Those are described in weighted/COMPATIBILITY_SUMMARY.md; they do not apply to the top-level original fitter or the unweighted result.
