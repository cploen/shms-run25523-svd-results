# Replay-compatible matrix format

The original emitted files had coefficient rows and a closing separator, but **no opening separator**. The weighted file's comment header did not supply that separator either.

HCANA's shared HMS/SHMS reader in THcHallCSpectrometer::ReadDatabase first skips leading `!` comments, then scans until `line.compare(0,4," ---")==0` before reading coefficient rows. Without an opening separator it scans through the coefficients to the closing line, then reaches EOF and reports an error with zero terms loaded.

The separator must begin with **one ASCII space followed by at least three hyphens**. Underscores, no leading space, or two leading spaces do not match this reader's literal prefix. There must be no blank non-coefficient lines inside the coefficient block, and the closing separator must remain newline-terminated.

## Minimal repair

- Insert one ` ---------------------------------------------` line immediately before the first coefficient row in each fitted matrix.
- Restore the existing, previously commented separator-write statement in fit_opt_matrix_gmm.C, so subsequent output uses the same envelope.
- Leave coefficient/exponent text, order, all 132 rows, final separator, numerical fitting code, ROOT truncation, event selection, targets, offsets and plots unchanged.

The direct before/after comparison verified every coefficient row byte-for-byte. Only each file's overall text hash changes. Earlier plot-generation hashes are retained separately in unweighted/diagnostic_inputs.json for provenance.

The exact writer change is in reference/replay_format.diff. The historical reference fitter remains untouched.

## Working controls

Compared with cploen/nps_replay at commit `82f6fa3bc8aae79298b649a8e83523c6ee39797a`, including:

- DATFILES/nps_hms_optics_5p878_ang.dat
- DATFILES/nps_hms_optics_6p117_ang.dat
- DATFILES/nps_hms_optics_6p667_ang.dat

Each uses the same space-plus-dashes envelope. The supplied SHMS base_matrix.dat also uses that format. The HMS reference controls use the same shared reader as SHMS.

## Checks performed

`tests/check_replay_matrix_format.py` extracts the **verbatim file-reading block** from THcHallCSpectrometer::ReadDatabase at HCANA commit `fcef8e23e16228fbb930078b9c44ef5031bed4f9`. A small standalone C++ harness supplies only the surrounding class fields, ROOT primitive typedefs, and an error-message sink. File reading, comment handling, separator comparisons, sscanf coefficient parsing, and reader return logic are unchanged. No ROOT or full HCANA build is needed.

Successful cases, with every parsed value/exponent and its order checked independently:

| File | Terms read |
|---|---:|
| Weighted output | 132 |
| Unweighted output | 132 |
| Supplied SHMS starting matrix | 131 |
| Each of the three working nps_replay controls | 461 |
| Test output from the actual current writer block | 3 |

Negative cases correctly fail: missing opening separator, two leading spaces, underscores in place of dashes, and a missing final newline. The missing-separator case reproduces the original defect.

The test also compiles and executes the **verbatim coefficient-output block** from the current fitter on a small coefficient fixture and passes that generated file back through the HCANA reader. This tests the writer correction without rerunning a fit.

Reproduce with Python 3 and g++, using existing checkouts:

    python3 tests/check_replay_matrix_format.py --hcana /path/to/hcana --nps-replay /path/to/nps_replay --report replay_format_validation.json

Machine-readable results and before/after hashes are in replay_format_validation.json.

## Scope

This verifies matrix-file readability through the tested HCANA parser and preservation of all matrix values. **No full HCANA event replay or test in the other group's replay repository was performed.** Their exact HCANA revision/configuration is unknown. No physics or reconstruction claims beyond the existing fit checks are added.

The original distinction in replay offsets still applies: weighted output retains external pphi_offset=-0.0008681269905 rad once; unweighted output uses external pphi_offset=0 because its fitted constant absorbs it. The formatting repair does not change that convention.
