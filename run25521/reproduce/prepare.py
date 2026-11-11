"""Construct documented geometry targets and balanced native-selection inputs. No fit."""
import sys,json
from pathlib import Path
import numpy as np
import uproot
repo=Path(__file__).resolve().parents[2]; out=repo/'run25521'
sys.path.insert(0,str(repo/'diagnostics'))
from make_unweighted_plots import evaluate
source=Path(sys.argv[1]); work=Path(sys.argv[2]); work.mkdir(parents=True,exist_ok=True)
p=np.load(source/'data_1.npz',allow_pickle=False); a={k:p[k] for k in p.files}; n=len(a['run'])
g=json.loads((repo/'config/geometry.json').read_text()); g.update(run=25521,foil_z_cm_by_rank={'0':10,'1':0,'2':-10},foil_evidence='User confirms previous-run geometry with additional foils; foil order from this handoff README.',installed_plate_pose_for_run25521='Inherited nominal centered geometry, not independently surveyed',authorization='User: it is the same as the previous run, just with more foils.')
g.pop('installed_plate_pose_for_run25523',None)
g['geometry_status']='User-authorized inheritance of prior nominal geometry with three nominal foils; no new survey or physical validation.'
g['scope']='Run 25521 angular SVD: fit xptar/ytar/yptar including constant; keep delta and xtar-dependent terms fixed; preserve candidate labels.'
(out/'config/geometry.json').write_text(json.dumps(g,indent=2)+'\n')
# Exact equations from historical handoff/build_tfit.py (5f825b5), applied once.
z=np.array([g['foil_z_cm_by_rank'][str(int(v))] for v in a['foil_id']],dtype=float)
theta=np.deg2rad(g['theta_deg']); bx=a['beam_x_cm']; by=a['beam_y_cm']; d=a['delta_percent']
xv=-by-g['mispoint_x_cm']; yv=-z*np.sin(theta)+bx*np.cos(theta)-g['mispoint_y_cm']; zv=z*np.cos(theta)+bx*np.sin(theta)
xs=g['hole_pitch_cm'][0]*a['hole_col']; ys=g['hole_pitch_cm'][1]*a['hole_row']
hb=g['hb_delta_polynomial_cm'][0]*d+g['hb_delta_polynomial_cm'][1]*d*d
xp=(xs-xv)/(g['sieve_z_cm']-zv); yp=(ys-hb-yv)/(g['sieve_z_cm']-zv)
xt=xv-xp*zv; yt=yv-yp*zv
closure=[float(np.max(abs(xt+xp*253-xs))),float(np.max(abs(yt+yp*253+hb-ys))),float(np.max(abs(xt+xp*zv-xv))),float(np.max(abs(yt+yp*zv-yv)))]
assert max(closure)<1e-11
blocked={f'{c},{r}':int(np.sum((a['hole_col']==c)&(a['hole_row']==r))) for c,r in g['blocked_holes']}; assert not any(blocked.values())
bounds=g['hole_index_bounds']; assert np.all((a['hole_col']>=bounds[0])&(a['hole_col']<=bounds[1])&(a['hole_row']>=bounds[0])&(a['hole_row']<=bounds[1]))
table=dict(a)
for dest,src in dict(xfp='fp_x_cm',xpfp='fp_xp_rad',yfp='fp_y_cm',ypfp='fp_yp_rad',delta='delta_percent',ztar='z_reco_cm',xptar='reco_xptar_rad',yptar='reco_yptar_rad',ytar='reco_ytar_cm').items(): table[dest]=a[src].copy()
table.update(xtar=xt,xtarT=xt,ytarT=yt,xptarT=xp,yptarT=yp,ztarT=z,xsT=xs,ysT=ys,vertex_x_transport=xv,vertex_y_transport=yv,vertex_z_transport=zv,hb_y_correction_cm=hb)
table['xs']=a['reco_xtar_cm']+253*a['reco_xptar_rad']; table['ys']=a['reco_ytar_cm']+253*a['reco_yptar_rad']+hb
# Verify THIS handoff's starting reconstruction/offset, at its stored replay xtar.
check={k:table[k] for k in ['xfp','xpfp','yfp','ypfp']}; check['xtar']=a['reco_xtar_cm']
old=evaluate(repo/'config/base_matrix.dat',check)
expected=np.column_stack([a['reco_xptar_rad'],a['reco_ytar_cm']/100,a['reco_yptar_rad']]); offset=np.array([g['xptar_external_offset_rad'],0,g['yptar_external_offset_rad']])
readback=np.max(abs(old+offset-expected),axis=0); assert max(readback)<1e-12
# Mirror the legacy gate, edges, foil lookup and y-sieve-column lookup in source order.
edges=np.array([-25,-6,-2,2,6,10,22.]); cells=np.zeros((3,6,11),dtype=int); eligible=np.zeros(n,bool); native=np.zeros(n,bool)
for i in range(n):
 nd=int(np.searchsorted(edges,d[i],side='right')-1); ny=int(a['hole_row'][i])+5; nf=int(a['foil_id'][i])
 if abs(d[i])<100 and -15<d[i]<30 and 0<=nd<6 and 0<=ny<11 and abs(ys[i]-(ny-5)*1.64)<.5:
  eligible[i]=True
  if cells[nf,nd,ny]<1000:
   native[i]=True; cells[nf,nd,ny]+=1
native_by=[int(np.sum(native&(a['foil_id']==f))) for f in range(3)]; limit=min(native_by)
selected=np.zeros(n,bool)
for f in range(3): selected[np.flatnonzero(native&(a['foil_id']==f))[:limit]]=True
idx=np.flatnonzero(selected)
assert len(idx)==3*limit
# Same previous-run supplied formula, recomputed on actual fitted population.
identities=np.column_stack([a['foil_id'][idx],a['hole_col'][idx],a['hole_row'][idx],np.floor(d[idx])])
unique,inverse,counts=np.unique(identities,axis=0,return_inverse=True,return_counts=True)
w=1/counts[inverse].astype(float); w/=w.mean()
assert np.allclose(np.bincount(inverse,weights=w),w.sum()/len(unique))
selected_table={k:np.asarray(v[idx]) for k,v in table.items()}; selected_table['fit_weight']=w
# Keep original arrays, names, values, types and ordering; added aliases/targets are Double_t.
for name in ['all','balanced']:
 path=work/'SHMS_run25521'/name; path.mkdir(parents=True,exist_ok=True)
 data=table if name=='all' else selected_table
 with uproot.recreate(path/'Optics_25521_-1_fit_tree_gmm.root') as f: f.mktree('TFit',data); f['geometry_json']=json.dumps(g)
 with uproot.open(path/'Optics_25521_-1_fit_tree_gmm.root') as f:
  reread=f['TFit'].arrays(library='np')
  for k in a: assert np.array_equal(reread[k],a[k] if name=='all' else a[k][idx]),k
np.savez(work/'selection.npz',indices=idx,eligible=eligible,native=native,weights=w)
report={'events':n,'target_geometry_closure_max_cm':closure,'starting_matrix_readback_max_abs_slope_m_slope':readback.tolist(),'confirmed_starting_external_offsets':offset.tolist(),'blocked_hole_counts':blocked,'edges_percent':edges.tolist(),'native_bin_cap':1000,'foil_balancing_limit_derived_from_native_populations':limit,'input_row_order_preserved':True,'fit_events':len(idx),'held_out_events':0,'foil_counts':{},'weight_definition':'w_i=(1/n_cell)/mean(1/n_cell), cells=(foil_id,hole_col,hole_row,floor(delta_percent/1%)); counts recomputed on identical fitted sample; each occupied cell has equal total weight','weight_range':[float(w.min()),float(w.max())],'occupied_weight_cells':len(unique),'selected_delta_sieve_counts':[], 'native_delta_sieve_counts':cells.tolist()}
for f in range(3):
 mask=a['foil_id']==f
 report['foil_counts'][str(f)]={'z_cm':g['foil_z_cm_by_rank'][str(f)],'available':int(mask.sum()),'eligible_before_bin_cap':int(np.sum(eligible&mask)),'native_after_bin_cap':native_by[f],'fitted_each_case':limit,'weight_sum':float(w[a['foil_id'][idx]==f].sum()),'occupied_weight_cells':int(np.sum(unique[:,0]==f))}
selected_cells=np.zeros_like(cells)
for i in idx: selected_cells[int(a['foil_id'][i]),int(np.searchsorted(edges,d[i],side='right')-1),int(a['hole_row'][i])+5]+=1
report['selected_delta_sieve_counts']=selected_cells.tolist()
(out/'selection.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'config/SHMS_run25521/optics_metadata.dat').write_text('25521,run25521,13.505,3,1,7\n10,0,-10\n-25,-6,-2,2,6,10,22\n')
(out/'config/SHMS_run25521/rungroups_inputs.tsv').write_text('rungroup\toptics_id\nrun25521\t25521\n')
print(json.dumps(report['foil_counts'],indent=2)); print('fit events',len(idx))
