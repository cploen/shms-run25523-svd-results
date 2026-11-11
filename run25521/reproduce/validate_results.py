"""Validate results without performing any numerical fit."""
from pathlib import Path
import sys,json,re,hashlib
import numpy as np
import uproot,fitz
from check_values import read_rows
repo=Path(__file__).resolve().parents[2]; out=repo/'run25521'; work=Path(sys.argv[1]); n=json.loads((out/'selection.json').read_text())['fit_events']
with uproot.open(work/'SHMS_run25521/balanced/Optics_25521_-1_fit_tree_gmm.root') as f: a=f['TFit'].arrays(library='np')
base=read_rows(repo/'config/base_matrix.dat'); terms=['00000']+[exp for exp in base if exp[-1]=='0']
v=np.column_stack([a['xfp']/100,a['xpfp'],a['yfp']/100,a['ypfp'],a['xtar']/100])
# Spot-check accumulated normal elements independently; no decomposition or solve.
check_indices=[(0,0),(0,1),(0,125),(4,18),(35,35),(74,102),(125,125)]
result={'ROOT_version':'6.40.00','full_HCANA_replay':False,'cases':{}}
for case,label in [('unweighted','Unweighted legacy fit'),('weighted','Supplied weights')]:
 path=out/case/'matrices'/f'nps_shms_newfit_25521_{case}.dat'; content=path.read_bytes(); lines=content.decode().splitlines(); rows=read_rows(path)
 assert lines[0].startswith(' ---') and lines[-1].startswith(' ---') and content.endswith(b'\n')
 assert all(line.strip() for line in lines[1:-1]); assert len(rows)==132
 info={'matrix_sha256':hashlib.sha256(content).hexdigest(),'separator_and_newline_checks':True,'rows':len(rows),'normal_element_checks':[],'pdf_pages':{},'diagnostic_entries':{}}
 with uproot.open(out/case/'root'/f'fit_opt_matrix_25521_{case}_qa.root') as f:
  normal=f['normal_matrix'].member('fElements').reshape((126,126)); w=a['fit_weight'] if case=='weighted' else np.ones(n)
  for i,j in check_indices:
   exps=np.array(list(map(int,terms[i])))+np.array(list(map(int,terms[j])))
   expected=float(np.sum(np.prod(v**exps,axis=1)*w)); actual=float(normal[i,j])
   error=abs(expected-actual); assert error<=1e-11*max(abs(expected),1e-18),(case,i,j,expected,actual)
   info['normal_element_checks'].append({'i':i,'j':j,'cpp_value':actual,'independent_sum':expected,'absolute_difference':error})
  for col,name in enumerate(['xptar','ytar','yptar']):
   solution=f[f'solution_{name}'].member('fElements')
   assert all(rows[exp][col]==float(format(solution[i],'.9g')) for i,exp in enumerate(terms))
  info['emitted_coefficients_match_native_solutions_at_legacy_9_digit_precision']=True
 for side in ['old','new']:
  for axis,pattern in [('xptar',r'hXpDiff_XpTrue_\d+_DelCut_\d+'),('yptar',r'hYpDiff_YpTrue_\d+_DelCut_\d+'),('ytar',r'hYDiff_YTrue_\d+_DelCut_\d+')]:
   p=out/case/'plots'/side/f'25521_{side}_{axis}_residuals.root'
   with uproot.open(p) as f: count=sum(float(f[key].member('fEntries')) for key in f.keys(cycle=False) if re.fullmatch(pattern,key))
   assert count==n,(case,side,axis,count); info['diagnostic_entries'][f'{side}_{axis}']=int(count)
 for p in sorted((out/case/'plots').rglob('*.pdf')):
  if any(part.startswith('foil_') for part in p.parts): continue # Expanded suite has separate validation.
  with fitz.open(p) as doc:
   assert len(doc)>0
   for page in doc: assert label in page.get_text(),str(p)
   info['pdf_pages'][str(p.relative_to(out/case))]=len(doc)
 assert len(info['pdf_pages'])==16,(case,len(info['pdf_pages']))
 for side in ['old','new']:
  assert all(info['pdf_pages'][f'plots/{side}/25521_{side}_{axis}_residuals_by_sieve.pdf']>0 for axis in ['xptar','ytar','yptar'])
 info['matching_events_old_new']=True
 result['cases'][case]=info
(out/'validation.json').write_text(json.dumps(result,indent=2)+'\n'); print('PASS: normal sums, native coefficient values, parser delimiters, diagnostic populations, all PDF pages and labels')
