"""Audit recorded-order selection and separate native-cap versus foil-total effects."""
from pathlib import Path
import sys,json
import numpy as np,uproot
repo=Path(__file__).resolve().parents[2];out=repo/'run25521';source=Path(sys.argv[1]);work=Path(sys.argv[2])
p=np.load(source/'data_1.npz',allow_pickle=False);s=np.load(work/'selection.npz');n=len(p['run']);idx=s['indices'];d=p['delta_percent'];foil=p['foil_id'];entry=p['source_full_entry'];eligible=s['eligible'];native=s['native'];selected=np.zeros(n,bool);selected[idx]=True
assert np.all(np.diff(entry)>0) and np.all(np.diff(idx)>0)
limit=24396;edges=np.array([-25.,-6.,-2.,2.,6.,10.,22.]);cells=np.zeros((3,6,11),int);totals=np.zeros(3,int);singlepass=[]
for i in range(n):
 nf=int(foil[i]);nd=np.searchsorted(edges,d[i],side='right')-1;ny=int(p['hole_row'][i])+5
 if -15<d[i]<30 and 0<=nd<6 and 0<=ny<11 and cells[nf,nd,ny]<1000 and totals[nf]<limit:
  singlepass.append(i);cells[nf,nd,ny]+=1;totals[nf]+=1
assert np.array_equal(np.array(singlepass),idx)
with uproot.open(work/'SHMS_run25521/balanced/Optics_25521_-1_fit_tree_gmm.root') as f:
 a=f['TFit'].arrays(['source_full_entry'],library='np')
assert np.array_equal(a['source_full_entry'],entry[idx])
report={'source_entries_strictly_increasing':True,'selected_indices_strictly_increasing':True,'balanced_tree_provenance_exactly_matches_selected_source_order':True,'single_pass_native_bin_and_foil_cap_scan_exactly_matches_two_stage_preparation':True,'randomization':False,'delta_sorting':False,'foil_cap':limit,'foil_counts':{},'near_minus6_counts':[]}
for f in range(3):
 mask=foil==f;keep=np.flatnonzero(selected&mask);before=np.flatnonzero(native&mask)
 assert np.array_equal(keep,before[:limit])
 report['foil_counts'][str(f)]={'available':int(mask.sum()),'eligible':int(np.sum(mask&eligible)),'native_bin_capped':len(before),'fitted':len(keep),'removed_by_extra_foil_total_cap':len(before)-len(keep),'last_selected_input_row_zero_based':int(keep[-1]),'last_selected_source_full_entry':int(entry[keep[-1]]),'last_native_source_full_entry':int(entry[before[-1]])}
for f in [None,0,1,2]:
 for lo,hi in [(-7,-6),(-6,-5)]:
  mask=(d>=lo)&(d<hi)
  if f is not None:mask&=foil==f
  counts={name:int(np.sum(mask&stage)) for name,stage in [('available',np.ones(n,bool)),('eligible',eligible),('native_bin_capped',native),('fitted',selected)]}
  report['near_minus6_counts'].append({'foil':f,'delta_low':lo,'delta_high':hi,**counts})
(out/'selection_order_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
