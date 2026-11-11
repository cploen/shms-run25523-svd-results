"""Read-only handoff audit; no target construction, selection, or fitting."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import uproot
source=Path(sys.argv[1]); destination=Path(sys.argv[2])
a=np.load(source/'data_1.npz',allow_pickle=False)
report={'fit_started':False,'source_sha256':{name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in ['data_1.root','data_1.npz']}}
with uproot.open(source/'data_1.root') as f:
 report['root_objects']=f.classnames()
 t=f['train']; report['root_entries']=t.num_entries
 b=t.arrays(library='np')
 if b.dtype.names if isinstance(b,np.ndarray) else False: b={k:b[k] for k in b.dtype.names}
 report['root_typenames']=t.typenames()
 report['same_fields']=set(a.files)==set(b)
 report['root_npz_equal']={k:bool(np.array_equal(a[k],b[k],equal_nan=True)) for k in a.files}
report['fields']={k:{'dtype':str(a[k].dtype),'finite':int(np.isfinite(a[k]).sum()),'min':a[k].min().item(),'max':a[k].max().item()} for k in a.files}
report['foil_populations']={str(i):int((a['foil_id']==i).sum()) for i in np.unique(a['foil_id'])}
report['split_populations_ignored']={str(i):int((a['split']==i).sum()) for i in np.unique(a['split'])}
report['clusters']=int(len(np.unique(a['cluster_id'])))
report['candidate_joint_identities']=int(len(np.unique(a['joint_class_id'])))
report['duplicate_source_keys']=int(len(a['run'])-len(np.unique(np.rec.fromarrays([a['run'],a['source_full_entry']]))))
report['flags']={k:int(a[k].sum()) for k in a.files if a[k].dtype.kind=='b'}
report['native_delta_gate_only_by_foil']={str(i):int(((a['foil_id']==i)&(a['delta_percent']>-15)&(a['delta_percent']<30)).sum()) for i in np.unique(a['foil_id'])}
report['eligible_counts_determined']=False
report['fitted_counts_by_foil']={str(i):0 for i in np.unique(a['foil_id'])}
report['missing_legacy_branches']=[k for k in ['ys','ysT','xtar','xtarT','xptar','yptar','ytar','xptarT','yptarT','ytarT','ztarT','delta','xpfp','ypfp','xfp','yfp'] if k not in b]
destination.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['fields','root_typenames','root_npz_equal']},indent=2))
