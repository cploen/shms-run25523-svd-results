#!/usr/bin/env bash
set -euo pipefail
# Dependencies: Python numpy/uproot/PyMuPDF/pypdf and ROOT (root executable).
# Usage: bash run25521/reproduce/run.sh EXTRACTED_ZIP_DIR WORK_DIR HCANA_SOURCE
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
source_dir="$(realpath "${1:?Extracted input directory required}")"
mkdir -p "${2:?Work directory outside the checkout required}"
work_dir="$(realpath "$2")"
hcana_dir="$(realpath "${3:?HCANA source checkout required (no build)}")"
cd "$repo_dir"
python run25521/reproduce/prepare.py "$source_dir" "$work_dir"
python run25521/reproduce/adapt_fitter.py
fit_count="$(python -c 'import json; print(json.load(open("run25521/selection.json"))["fit_events"])')"
for case_name in unweighted weighted; do
  case_dir="$repo_dir/run25521/$case_name"
  mkdir -p "$case_dir/matrices" "$case_dir/root"
  weighted_arg=false
  if [[ "$case_name" == weighted ]]; then weighted_arg=true; fi
  root -l -b -q "run25521/reproduce/fit_run25521.C+(\"25521_${case_name}\",-1,${fit_count},-1,\"${work_dir}/SHMS_run25521/balanced\",\"${case_dir}\",\"${repo_dir}/config/base_matrix.dat\",\"${repo_dir}/run25521/config/SHMS_run25521/rungroups_inputs.tsv\",\"${repo_dir}/run25521/config/SHMS_run25521/optics_metadata.dat\",${weighted_arg})" > "$case_dir/run.log" 2>&1
done
python run25521/reproduce/diagnostics.py "$work_dir"
python diagnostics/label_plot_pdfs.py run25521/unweighted/plots run25521/unweighted/plots/old run25521/unweighted/plots/new --label 'Unweighted legacy fit'
python diagnostics/label_plot_pdfs.py run25521/weighted/plots run25521/weighted/plots/old run25521/weighted/plots/new --label 'Supplied weights'
python tests/check_replay_matrix_format.py --hcana "$hcana_dir" --matrix "$repo_dir/run25521/unweighted/matrices/nps_shms_newfit_25521_unweighted.dat" --matrix "$repo_dir/run25521/weighted/matrices/nps_shms_newfit_25521_weighted.dat" --report run25521/replay_format_validation.json
python run25521/reproduce/validate_results.py "$work_dir"
python run25521/reproduce/foil_slice_diagnostics.py "$work_dir"
python run25521/reproduce/validate_foil_slices.py
python run25521/reproduce/index_foil_slices.py
python run25521/reproduce/run_nps_legacy.py "$work_dir"

python run25521/reproduce/plot_delta_vs_ytar.py "$work_dir"
python run25521/reproduce/plot_delta_vs_ytar_comparison.py "$work_dir"
python run25521/reproduce/plot_delta_histograms.py "$work_dir"
