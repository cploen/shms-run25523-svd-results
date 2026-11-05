#!/usr/bin/env bash
set -euo pipefail
# ROOT/PyROOT and Python numpy/uproot must already be installed and active.
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source_root="${1:?Usage: bash run_unweighted.sh /path/to/shms_25523_data_0_fit.root}"
input_dir="$repo_dir/SHMS_run25523/trees"
mkdir -p "$input_dir"
python3 "$repo_dir/prepare_input.py" "$source_root" "$input_dir/Optics_25523_-1_fit_tree_gmm.root"
root -l -b -q "$repo_dir/fit_opt_matrix_gmm.C+(\"25523_unweighted\",-1,433019,-1,\"$input_dir\",\"$repo_dir/unweighted\",\"$repo_dir/config/base_matrix.dat\",\"$repo_dir/config/SHMS_run25523/rungroups_inputs.tsv\",\"$repo_dir/config/SHMS_run25523/optics_metadata.dat\")" > "$repo_dir/unweighted/run.log" 2>&1
