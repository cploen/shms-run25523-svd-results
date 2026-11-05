from pathlib import Path
import subprocess,json
b=Path('/workspace/shms_run25523'); out=b/'result_root_legacy'; diag=out/'SHMS_run25523'; diag.mkdir(parents=True,exist_ok=True)
audit=json.loads((b/'result_student_weights/audit.json').read_text())
# These are plotting intervals only. Include all input deltas, without extra selection.
edges=[-10.,-6.,-2.,2.,6.,10.,22.]
lo,hi=audit['delta_range_percent']; edges[0]=min(edges[0],lo-.001); edges[-1]=max(edges[-1],hi+.001)
metadata=diag/'optics_metadata.dat'
metadata.write_text('25523,run25523,13.505,1,1,7\n0\n'+','.join(map(str,edges))+'\n')
root='/workspace/.optics/venv/lib/python3.12/site-packages/ROOT/bin/root'
for label in ['old','new']:
 for axis in ['xptar','yptar','ytar']:
  macro=b/'legacy_code/diagnostics/fit'/f'plot_{axis}_residuals.C'
  plots=out/'plots'/label; plots.mkdir(exist_ok=True)
  expression=f'{macro}(25523,"{diag/ (label+".root")}","{metadata}","{plots}","25523_{label}")'
  with (out/f'legacy_{label}_{axis}.log').open('w') as log:
   r=subprocess.run([root,'-l','-b','-q',expression],stdout=log,stderr=subprocess.STDOUT)
  print(label,axis,r.returncode,flush=True)
  if r.returncode: raise RuntimeError(f'{label} {axis} failed: see log')
