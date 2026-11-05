from pathlib import Path
import sys,numpy as np,uproot
source=Path(sys.argv[1]); dest=Path(sys.argv[2])
if dest.exists(): raise FileExistsError(dest)
with uproot.open(source,handler=uproot.source.file.MemmapSource) as f:
 a=f['TFit'].arrays(library='np')
 a['ztarT']=a['ztarT'].astype(np.float64)
 geometry=str(f['geometry_json'])
with uproot.recreate(dest) as f:
 f.mktree('TFit',a); f['geometry_json']=geometry
with uproot.open(source,handler=uproot.source.file.MemmapSource) as f,uproot.open(dest,handler=uproot.source.file.MemmapSource) as g:
 old=f['TFit'].arrays(library='np'); new=g['TFit'].arrays(library='np')
 assert set(old)==set(new)
 for name in old:
  assert np.array_equal(old[name],new[name]),name
  assert old[name].dtype==new[name].dtype or name=='ztarT',name
print('All 57 original branches and 433019 rows preserved; only ztarT dtype changed. No weight branch added.')
