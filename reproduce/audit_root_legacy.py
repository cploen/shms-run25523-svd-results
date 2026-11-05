from pathlib import Path
import sys,json,zipfile,re,subprocess
import numpy as np,uproot
b=Path('/workspace/shms_run25523'); out=b/'result_root_legacy'; sys.path.insert(0,str(b)); import run_svd_student_weights as pyfit
source=b/'handoff/shms_25523_data_0_fit.root'; data,_=pyfit.read_tfit(source)
with uproot.open(source,handler=uproot.source.file.MemmapSource) as f: a=f['TFit'].arrays(library='np')
_,old=pyfit.read_matrix(b/'handoff/base_matrix.dat'); matrix=out/'matrices/nps_shms_newfit_25523_legacy.dat'; _,new=pyfit.read_matrix(matrix)
oldmap={k:v for _,k,v in old}; newmap={k:v for _,k,v in new}
assert len(newmap)==len(new)
for k,v in oldmap.items():
 assert newmap[k][3]==v[3],('delta',k)
 if k[-1]!='0': assert np.array_equal(newmap[k],v),('fixed xtar',k)
oldpred=pyfit.powers(data,old)@np.stack([v[:3] for _,_,v in old])+[-8.681269905e-4,0,0]
newpred=pyfit.powers(data,new)@np.stack([v[:3] for _,_,v in new])+[-8.681269905e-4,0,0]
truth=np.column_stack([a['xptarT'],a['ytarT']/100,a['yptarT']]); replay=np.column_stack([a['xptar'],a['ytar']/100,a['yptar']])
weights,mode=pyfit.weights(data,np.ones(len(truth),dtype=bool),1.)
solver=json.loads((out/'solver.json').read_text()); assert solver['events']==len(truth)
log=(b/'root_legacy.log').read_text()
assert 'Error in <' not in log, log
assert 'number to fit = 433019 max = 433019' in log
for n in ['xptar','yptar','ytar']: assert n+' solution ok = 1' in log
metrics={label:pyfit.metrics(truth,pred) for label,pred in [('starting_same_xtarT',oldpred),('new_root_legacy',newpred),('original_replay',replay)]}
weighted={label:(np.sqrt(np.average((pred-truth)**2,weights=weights,axis=0))*1000).tolist() for label,pred in [('starting_same_xtarT',oldpred),('new_root_legacy',newpred)]}
with uproot.open(out/'root/fit_opt_matrix_25523_legacy_qa.root',handler=uproot.source.file.MemmapSource) as f:
 for name in ['hytardiff','hyptardiff','hxptardiff','hytarnewdiff','hyptarnewdiff','hxptarnewdiff']:
  assert f[name].member('fEntries')==len(truth),(name,f[name].member('fEntries'))
report={'solver':'Repository legacy ROOT TDecompSVD on unscaled X^T W X; weights applied once','repository_ref':'hms-shms-campaign-switch 21c5d8e439a16e440ecd0307fa20a086d550d143','solver_details':solver,'balancing':mode,'fit_events':len(truth),'held_out_events':0,'delta_and_xtar_dependent_rows_preserved':True,'xptar_geometry_changed':False,'external_xptar_offset_rad':-8.681269905e-4,'metrics_units':['slope','m','slope'],'unweighted_metrics':metrics,'weighted_rmse_mrad_mm_mrad':weighted}
(out/'fit_report.json').write_text(json.dumps(report,indent=2)+'\n')
np.savez(out/'predictions.npz',truth=truth,fitted=newpred,baseline=oldpred)
# Legacy residual macros evaluate the emitted text matrix, including its precision.
diag=out/'SHMS_run25523'; diag.mkdir(exist_ok=True)
needed=['ys','xs','ysT','xsT','xtar','ztar','xptar','yptar','ytar','xptarT','yptarT','ytarT','ztarT','delta','xpfp','ypfp','xfp','yfp']
for label,values in [('old',oldpred),('new',newpred)]:
 table={k:np.asarray(a[k],dtype='float64') for k in needed}; table.update(xptar=values[:,0],ytar=values[:,1]*100,yptar=values[:,2])
 with uproot.recreate(diag/f'{label}.root') as f: f.mktree('TFit',table)
print(json.dumps(report,indent=2),flush=True)
