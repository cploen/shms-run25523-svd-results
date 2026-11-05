#!/usr/bin/env bash
set -euo pipefail
source /workspace/.optics/activate.sh
root -l -b -q '/workspace/shms_run25523/fit_opt_matrix_gmm_legacy.C+("25523_legacy",-1,433019,-1,"/workspace/shms_run25523/SHMS_legacy_25523/trees","/workspace/shms_run25523/result_root_legacy","/workspace/shms_run25523/handoff/base_matrix.dat","/workspace/shms_run25523/SHMS_legacy_25523/rungroups_inputs.tsv","/workspace/shms_run25523/SHMS_legacy_25523/optics_metadata.dat")' > /workspace/shms_run25523/root_legacy.log 2>&1
OPENBLAS_NUM_THREADS=4 python /workspace/shms_run25523/audit_root_legacy.py > /workspace/shms_run25523/audit_root_legacy.log 2>&1
python /workspace/shms_run25523/run_root_legacy_plots.py > /workspace/shms_run25523/legacy_root_plots.log 2>&1
python /workspace/shms_run25523/package_root_legacy.py
