from pathlib import Path
import sys,difflib,json
import numpy as np,uproot
b=Path('/workspace/shms_run25523'); sys.path.insert(0,str(b)); import run_svd_student_weights as pyfit
campaign=b/'SHMS_legacy_25523'; trees=campaign/'trees'; trees.mkdir(parents=True,exist_ok=True)
source=b/'handoff/shms_25523_data_0_fit.root'
data,_=pyfit.read_tfit(source); weights,mode=pyfit.weights(data,np.ones(len(data['xfp']),dtype=bool),1.)
with uproot.open(source,handler=uproot.source.file.MemmapSource) as f: a=f['TFit'].arrays(library='np')
# Legacy SetBranchAddress expects Double_t for ztarT; preserve its exact numeric zeros.
a['ztarT']=a['ztarT'].astype(np.float64)
a['fit_weight']=weights
with uproot.recreate(trees/'Optics_25523_-1_fit_tree_gmm.root') as f: f.mktree('TFit',a); f['geometry_json']=(b/'handoff/geometry.json').read_text()
(campaign/'rungroups_inputs.tsv').write_text('rungroup\toptics_id\nrun25523\t25523\n')
(campaign/'optics_metadata.dat').write_text('25523,run25523,13.505,1,1,7\n0\n-25,-6,-2,2,6,10,22\n')
original=(b/'fit_opt_matrix_gmm_reference.C').read_text(); s=original
s=s.replace('#include "spectrometer_root.h"','#include "legacy_code/spectrometer_root.h"\n#include <cmath>\n#include <TF1.h>\nusing namespace std;')
s=s.replace('void fit_opt_matrix_gmm(', 'void fit_opt_matrix_gmm_legacy(')
s=s.replace('  TMatrixD lambda(npar,nfit_max);','  TMatrixD lambda(npar,nfit_max);\n  vector<double> eventWeights;\n  const double xptarOffset = -8.681269905e-4;\n  const double yptarOffset = 0.0;')
s=s.replace('    //Declaration of leaves types','    Double_t fitWeight = 1.;\n    if (!FitTree->GetBranch("fit_weight")) throw std::runtime_error("Missing supplied weights");\n    FitTree->SetBranchAddress("fit_weight", &fitWeight);\n    //Declaration of leaves types')
s=s.replace('      if ( delta>-15. &&  delta<30. ) {','      if ( std::isfinite(delta) ) {')
old='if (good_bin && nfit < nfit_max && Ztar_Ys_Delta_Cnts[found_nf][found_nd][found_ny]< MaxPerBin && Ztar_Cnts[found_nf]< MaxZtarPerBin && Ztar_Cnts[found_nf]<Max_Per_Run_Per_Foil[found_nf])'
assert old in s
s=s.replace(old,'if (good_bin && nfit < nfit_max)')
s=s.replace('(xptarT-xptar_xtar) * etemp','(xptarT-xptarOffset-xptar_xtar) * etemp * fitWeight')
s=s.replace('(yptarT-yptar_xtar) * etemp','(yptarT-yptarOffset-yptar_xtar) * etemp * fitWeight')
s=s.replace('(ytarT-ytar_xtar*100) /100.0 * etemp','(ytarT-ytar_xtar*100) /100.0 * etemp * fitWeight')
s=s.replace('  nfit++;','  eventWeights.push_back(fitWeight);\n\t  nfit++;')
s=s.replace('Ay[ipar][jpar] += lambda[ipar][ifit] * lambda[jpar][ifit];','Ay[ipar][jpar] += eventWeights[ifit] * lambda[ipar][ifit] * lambda[jpar][ifit];')
s=s.replace('  TDecompSVD Ay_svd(Ay);','''  // Original legacy path: SVD of raw normal matrix. No column normalization,
  // direct-design SVD, custom tolerance or rank rescue is introduced.
  TDecompSVD Ay_svd(Ay);
  Ay_svd.Decompose();
  const TVectorD& sig=Ay_svd.GetSig();
  const double cutoff=Ay_svd.GetTol()*sig[0];
  int retained=0;
  ofstream spectrum(Form("%s/normal_matrix_spectrum.tsv",outputDir.Data()));
  spectrum << setprecision(17) << "index\\tsingular_value\\tretained\\n";
  for(int i=0;i<sig.GetNrows();++i) {
    const bool keep=(sig[i]>cutoff); retained+=keep;
    spectrum << i << "\\t" << sig[i] << "\\t" << keep << "\\n";
  }
  cout << setprecision(17) << "LEGACY_NORMAL_EQ terms=" << npar
       << " retained=" << retained << " tol=" << Ay_svd.GetTol()
       << " cutoff=" << cutoff << "\\n";
  ofstream info(Form("%s/solver.json",outputDir.Data()));
  info << setprecision(17) << "{\\"terms\\":" << npar << ",\\"retained\\":" << retained
       << ",\\"events\\":" << nfit << ",\\"root_tolerance\\":" << Ay_svd.GetTol()
       << ",\\"cutoff\\":" << cutoff << "}\\n";
''')
s=s.replace('hyptarnew->Fill(yptarnew+yptar_xtar);','hyptarnew->Fill(yptarnew+yptar_xtar+yptarOffset);')
s=s.replace('hxptarnew->Fill(xptarnew);','hxptarnew->Fill(xptarnew+xptar_xtar+xptarOffset);')
s=s.replace('yptarnew+yptar_xtar-yptartrue.at(ifit)','yptarnew+yptar_xtar+yptarOffset-yptartrue.at(ifit)')
s=s.replace('xptarnew+xptar_xtar-xptartrue.at(ifit)','xptarnew+xptar_xtar+xptarOffset-xptartrue.at(ifit)')
s=s.replace('  //newcoeffsfile << "! new fit to "','  newcoeffsfile << "! Legacy ROOT SVD of X^T W X; retain external pphi_offset=-0.0008681269905 rad once." << endl;\n  //newcoeffsfile << "! new fit to "')
assert 'eventWeights.push_back(fitWeight)' in s
(b/'fit_opt_matrix_gmm_legacy.C').write_text(s)
(b/'legacy_fitter_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='repository/fit_opt_matrix_gmm.C',tofile='fit_opt_matrix_gmm_legacy.C')))
print('Prepared',len(weights),'events with',mode)
