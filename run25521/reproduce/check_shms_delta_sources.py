"""Derive delta windows from archived upstream SHMS source excerpts, no fitting."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sources=json.loads((root/'audit/shms_delta_slice_sources.json').read_text())
def record(repo,path):return next(r for r in sources if r['repository']==repo and r['path']==path)
def numbers(s):return [float(v) for v in s.split(',') if v.strip()]
def config_windows(repo,path,run):
 r=record(repo,path);lines=r['full_text'].splitlines();i=next(i for i,s in enumerate(lines) if s.startswith(str(run)+','));centers=numbers(lines[i+2]);widths=numbers(lines[i+3]);assert len(centers)==len(widths)
 return dict(repository=repo,path=path,run=run,centers=centers,half_widths=widths,intervals_in_file_order=[[c-w,c+w] for c,w in zip(centers,widths)])
r=record('zwertz/SHMS_OPTICS','fit_opt_matrix.C');text='\n'.join(x['text'] for x in r['excerpts'])
c=numbers(re.search(r'delcut\[ndelcut\]=\{([^}]+)\}',text)[1]);w=numbers(re.search(r'delwidth\[ndelcut\]=\{([^}]+)\}',text)[1]);classic=[[x-y,x+y] for x,y in zip(c,w)]
assert classic==[[-12,-10],[-10,-6],[-6,-2],[-2,2],[2,6],[6,10],[10,25]]
z=config_windows('zwertz/SHMS_OPTICS','DATfiles/list_of_optics_run.dat',22045)
assert z['intervals_in_file_order']==[[-12,-6],[-6,-2],[-2,2],[2,10],[10,25]]
a=config_windows('hszumila/shms_optics_a1n','list_of_optics_run.dat',10776)
assert sorted(a['intervals_in_file_order'])==[[-13,-12],[-12,-11],[-11,-10],[-10,-8],[-8,-6],[-6,-2],[-2,2],[2,6],[6,10],[10,25]]
result={'current_run25521_edges':[-25,-6,-2,2,6,10,22],'current_run25521_effective_first_interval':[-15,-6],'classic_shared_zwertz_and_a1n_intervals':classic,'zwertz_run22045':z,'a1n_run10776':a,'selection_semantics':'lower bound inclusive, upper exclusive; assignment by center +/- half_width in upstream C macros','run25521_definition_found_in_these_files':False,'no_fit_or_selection_changed':True}
(root/'shms_delta_slice_comparison.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: upstream center/half-width interpretation and derived intervals verified')
