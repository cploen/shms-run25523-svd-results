"""Create a run-specific copy; preserve the tracked legacy source and solver."""
from pathlib import Path
import difflib
repo=Path(__file__).resolve().parents[2]; folder=Path(__file__).resolve().parent
s=(repo/'fit_opt_matrix_gmm.C').read_text(); original=s
s=s.replace('#include "spectrometer_root.h"','#include "../../spectrometer_root.h"\n#include <TF1.h>\n#include <cmath>\nusing namespace std;')
s=s.replace('void fit_opt_matrix_gmm(', 'void fit_run25521(')
s=s.replace('  TString opticsMetadataFile) {','  TString opticsMetadataFile,\n  Bool_t suppliedWeights=kFALSE) {')
s=s.replace('  vector<double> xtartrue,','  vector<double> eventWeights;\n  vector<double> xtartrue,')
s=s.replace('    //Declaration of leaves types','    Double_t fitWeight=1.;\n    if (suppliedWeights) FitTree->SetBranchAddress("fit_weight",&fitWeight);\n    //Declaration of leaves types')
s=s.replace('    FitTree->GetEntry(i);','    FitTree->GetEntry(i);\n    if (!(fitWeight>0.) || !std::isfinite(fitWeight)) { cout << "ERROR invalid weight" << endl; return; }')
s=s.replace('(xptarT-xptar_xtar) * etemp','(xptarT-xptar_xtar) * etemp * fitWeight')
s=s.replace('(yptarT-yptar_xtar) * etemp','(yptarT-yptar_xtar) * etemp * fitWeight')
s=s.replace('(ytarT-ytar_xtar*100) /100.0 * etemp','(ytarT-ytar_xtar*100) /100.0 * etemp * fitWeight')
s=s.replace('  nfit++;','  eventWeights.push_back(fitWeight);\n\t  nfit++;')
s=s.replace('lambda[ipar][ifit] * lambda[jpar][ifit]','lambda[ipar][ifit] * lambda[jpar][ifit] * eventWeights.at(ifit)')
s=s.replace('  bool ok;','  bool ok; bool ytarOK, yptarOK, xptarOK;')
s=s.replace('  ok = Ay_svd.Solve( b_ytar );','  ok = Ay_svd.Solve( b_ytar ); ytarOK=ok;')
s=s.replace('  ok = Ay_svd.Solve( b_yptar );','  ok = Ay_svd.Solve( b_yptar ); yptarOK=ok;')
s=s.replace('  ok = Ay_svd.Solve( b_xptar );','  ok = Ay_svd.Solve( b_xptar ); xptarOK=ok;')
needle='  //b_xptar.Print();'
assert needle in s
s=s.replace(needle,needle+'''
  const TVectorD singular=Ay_svd.GetSig();
  const double tol=Ay_svd.GetTol(), cutoff=tol*singular[0];
  int retained=0;
  ofstream spectrum(Form("%s/normal_matrix_spectrum.tsv",outputDir.Data()));
  spectrum << "mode\\tsingular_value\\tretained\\n" << setprecision(17);
  for (int k=0;k<npar;k++) { if(singular[k]>cutoff) retained++; spectrum << k << "\\t" << singular[k] << "\\t" << (singular[k]>cutoff) << "\\n"; }
  ofstream solver(Form("%s/solver.json",outputDir.Data()));
  solver << setprecision(17) << "{\\"events\\":" << nfit << ",\\"terms\\":" << npar
    << ",\\"retained\\":" << retained << ",\\"root_tolerance\\":" << tol << ",\\"cutoff\\":" << cutoff
    << ",\\"ytar_ok\\":" << ytarOK << ",\\"yptar_ok\\":" << yptarOK << ",\\"xptar_ok\\":" << xptarOK << "}\\n";
''')
# Legacy residual already adds the fixed xtar term; correct only distribution view.
s=s.replace('hxptarnew->Fill(xptarnew);','hxptarnew->Fill(xptarnew+xptar_xtar);')
s=s.replace('  hallc::writeProfile(spec);','  hallc::writeProfile(spec);\n  Ay.Write("normal_matrix");\n  b_xptar.Write("solution_xptar"); b_ytar.Write("solution_ytar"); b_yptar.Write("solution_yptar");')
(folder/'fit_run25521.C').write_text(s)
(folder/'legacy_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='fit_opt_matrix_gmm.C',tofile='run25521/reproduce/fit_run25521.C')))
