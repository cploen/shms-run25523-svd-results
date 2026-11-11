"""Evaluate emitted matrices for full legacy diagnostic macros; no fitting."""
from pathlib import Path
import sys,json,subprocess,concurrent.futures,hashlib
import numpy as np
import uproot
repo=Path(__file__).resolve().parents[2]; out=repo/'run25521'; work=Path(sys.argv[1])
sys.path.insert(0,str(repo/'diagnostics'))
from make_unweighted_plots import evaluate
with uproot.open(work/'SHMS_run25521/balanced/Optics_25521_-1_fit_tree_gmm.root') as f: a=f['TFit'].arrays(library='np')
sel=json.loads((out/'selection.json').read_text()); n=sel['fit_events']; assert len(a['delta'])==n
truth=np.column_stack([a['xptarT'],a['ytarT']/100,a['yptarT']]); w=a['fit_weight']
oldpath=repo/'config/base_matrix.dat'; old=evaluate(oldpath,a)+[-0.0008681269905,0,0]
needed=['ys','xs','ysT','xsT','xtar','ztar','xptar','yptar','ytar','xptarT','yptarT','ytarT','ztarT','delta','xpfp','ypfp','xfp','yfp']
def metrics(pred):
 r=(pred-truth)*1000
 return {'rmse_mrad_mm_mrad':np.sqrt(np.mean(r*r,axis=0)).tolist(),'supplied_weight_rmse_mrad_mm_mrad':np.sqrt(np.average(r*r,axis=0,weights=w)).tolist(),'mean_mrad_mm_mrad':np.mean(r,axis=0).tolist(),'abs_p95_mrad_mm_mrad':np.percentile(abs(r),95,axis=0).tolist()}
jobs=[]
for case in ['unweighted','weighted']:
 matrix=out/case/'matrices'/f'nps_shms_newfit_25521_{case}.dat'
 new=evaluate(matrix,a)
 # Fixed delta coefficients and every xtar-dependent coefficient preserved numerically.
 from check_values import read_rows
 base=read_rows(oldpath); fitted=read_rows(matrix)
 assert set(fitted)==set(base)|{'00000'}
 for exp,coeff in base.items():
  assert fitted[exp][3]==coeff[3],exp
  if exp[-1]!='0': assert fitted[exp]==coeff,exp
 assert fitted['00000'][3]==0
 report={'method':'Supplied weights' if case=='weighted' else 'Unweighted legacy fit','fit_events':n,'held_out_events':0,'selection_identical_between_cases':True,'external_offsets_for_output_matrix':[0,0,0],'offset_subtracted_before_fit':False,'delta_and_xtar_coefficients_preserved':True,'metrics_units':['mrad','mm','mrad'],'old_at_same_geometric_xtar':metrics(old),'new_at_same_geometric_xtar':metrics(new),'original_stored_reconstruction':metrics(np.column_stack([a['xptar'],a['ytar']/100,a['yptar']])),'solver':json.loads((out/case/'solver.json').read_text()),'full_HCANA_replay':False}
 with uproot.open(out/case/'root'/f'fit_opt_matrix_25521_{case}_qa.root') as f:
  report['automatic_summary_histogram_entries']={key:float(f[key].member('fEntries')) for key in ['hytardiff','hyptardiff','hxptardiff','hytarnewdiff','hyptarnewdiff','hxptarnewdiff']}
  assert set(report['automatic_summary_histogram_entries'].values())=={float(n)}
 for label,pred in [('old',old),('new',new)]:
  table={k:np.asarray(a[k],dtype=float) for k in needed}; table.update(xptar=pred[:,0],ytar=pred[:,1]*100,yptar=pred[:,2])
  path=work/'SHMS_run25521'/f'{case}_{label}.root'
  with uproot.recreate(path) as f: f.mktree('TFit',table)
  plotdir=out/case/'plots'/label; plotdir.mkdir(parents=True,exist_ok=True)
  for axis in ['xptar','yptar','ytar']:
   macro=repo/'diagnostics/fit'/f'plot_{axis}_residuals.C'
   expr=f'{macro}(25521,"{path}","{out}/config/SHMS_run25521/optics_metadata.dat","{plotdir}","25521_{label}")'
   jobs.append((case,label,axis,expr,plotdir/f'{axis}.log'))
 (out/case/'fit_report.json').write_text(json.dumps(report,indent=2)+'\n')
def run(job):
 case,label,axis,expr,log=job
 with log.open('w') as stream: subprocess.run(['root','-l','-b','-q',expr],stdout=stream,stderr=subprocess.STDOUT,check=True)
 text=log.read_text(); assert f'start loop {n}' in text,(case,label,axis)
 assert 'Error in <' not in text,(case,label,axis)
 print(case,label,axis,'PASS',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(run,jobs))
