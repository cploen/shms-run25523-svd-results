"""Evaluate the two matrices on the legacy-selected events and run original plot macros.

This is plotting/input preparation only. It does not fit or change a matrix.
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
import numpy as np
import uproot

ROW=re.compile(r'^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+([0-9]{5})\s*$')
def evaluate(path,a):
    v=np.column_stack([a['xfp']/100,a['xpfp'],a['yfp']/100,a['ypfp'],a['xtar']/100])
    out=np.zeros((len(v),3))
    for line in path.read_text().splitlines():
        match=ROW.fullmatch(line)
        if match:
            term=np.prod(v**np.array(list(map(int,match[5]))),axis=1)
            out+=term[:,None]*np.array([float(match[k]) for k in [1,2,3]])
    return out

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('workdir',type=Path,help='Temporary plotting inputs; must be outside the Git checkout')
    args=parser.parse_args()
    repo=Path(__file__).resolve().parents[1]
    report=json.loads((repo/'unweighted/fit_report.json').read_text())
    with uproot.open(args.input,handler=uproot.source.file.MemmapSource) as source:
        a=source['TFit'].arrays(library='np')
    # Mirror only the existing C++ selection; no new balancing or random split.
    edges=np.array([-25.,-6.,-2.,2.,6.,10.,22.])
    counts=np.zeros((6,11),int)
    indices=[]
    for i,d in enumerate(a['delta']):
        nd=np.searchsorted(edges,d,side='right')-1
        ny=int(a['hole_row'][i])+5
        if abs(d)<100 and -15<d<30 and abs(a['ztarT'][i])<2.5 and 0<=nd<6 and 0<=ny<11 and abs(a['ysT'][i]-(-8.2+1.64*ny))<.5:
            if counts[nd,ny]<1000 and len(indices)<433019:
                indices.append(i);counts[nd,ny]+=1
    idx=np.array(indices)
    assert len(idx)==report['fit_events']==50463
    assert np.array_equal(counts,np.array(report['accepted_delta_sieve_counts']))
    a={k:v[idx] for k,v in a.items()}
    old=repo/'config/base_matrix.dat'
    new=repo/'unweighted/matrices/nps_shms_newfit_25523_unweighted.dat'
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [old,new]}
    predictions={'old':evaluate(old,a)+[-0.0008681269905,0,0], 'new':evaluate(new,a)}
    work=args.workdir.resolve()/'SHMS_run25523'
    work.mkdir(parents=True,exist_ok=True)
    needed=['ys','xs','ysT','xsT','xtar','ztar','xptar','yptar','ytar','xptarT','yptarT','ytarT','ztarT','delta','xpfp','ypfp','xfp','yfp']
    for label,values in predictions.items():
        table={k:np.asarray(a[k],dtype='float64') for k in needed}
        table.update(xptar=values[:,0],ytar=values[:,1]*100,yptar=values[:,2])
        path=work/f'{label}.root'
        with uproot.recreate(path) as target: target.mktree('TFit',table)
        out=repo/'unweighted/plots'/label
        out.mkdir(exist_ok=True)
        for axis in ['xptar','yptar','ytar']:
            macro=repo/'diagnostics/fit'/f'plot_{axis}_residuals.C'
            metadata=repo/'config/SHMS_run25523/optics_metadata.dat'
            expression=f'{macro}(25523,"{path}","{metadata}","{out}","25523_{label}")'
            log=out/f'{axis}.log'
            with log.open('w') as stream:
                subprocess.run(['root','-l','-b','-q',expression],stdout=stream,stderr=subprocess.STDOUT,check=True)
            text=log.read_text()
            assert 'start loop 50463' in text,(label,axis)
            assert 'Error in <' not in text,(label,axis)
            print(label,axis,'PASS: 50463 selected events',flush=True)
    for p in [old,new]: assert hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p)]
    (repo/'unweighted/diagnostic_inputs.json').write_text(json.dumps({'events':len(idx),'selection':'same 50463 events as the unweighted fit','accepted_cell_counts_match_fit':True,'matrix_hashes':{str(Path(k).relative_to(repo)):v for k,v in hashes.items()},'old':'base matrix evaluated at supplied xtar/xtarT plus starting external xptar offset','new':'unweighted emitted matrix evaluated at supplied xtar/xtarT with zero external slope offsets','fresh_HCANA_replay':False,'plot_macro_commit':'3b93f6e3a25a4078fa73bc8f46ecf8624d4d0bba'},indent=2)+'\n')

if __name__=='__main__': main()
