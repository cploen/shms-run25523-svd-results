"""Expanded ROOT diagnostic displays, explicitly indexed by foil and delta slice.
No fitting, coefficient changes, event reselection, display offsets, or weights.
"""
from pathlib import Path
import sys,json,csv,hashlib
import numpy as np
import uproot
import ROOT
from pypdf import PdfReader,PdfWriter
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetTitleFontSize(.045)
ROOT.gStyle.SetPadLeftMargin(.14); ROOT.gStyle.SetPadRightMargin(.13)
repo=Path(__file__).resolve().parents[2]; out=repo/'run25521'; work=Path(sys.argv[1])
sel=json.loads((out/'selection.json').read_text()); edges=sel['edges_percent']; counts=np.array(sel['selected_delta_sieve_counts']).sum(axis=2)
zs=[10,0,-10]; foilnames=['foil_0_z_plus10','foil_1_z_0','foil_2_z_minus10']; slices=['delta_00_minus15_to_minus6','delta_01_minus6_to_minus2','delta_02_minus2_to_plus2','delta_03_plus2_to_plus6','delta_04_plus6_to_plus10','delta_05_plus10_to_plus22']
axes=['xptar','ytar','yptar']; units=['mrad','cm','mrad']; ranges=[20,5,20]
report={'description':'Expanded ROOT displays on the existing selected matrix-evaluation inputs, no refit','fit_events':sel['fit_events'],'case_side_foil_slices':[],'matrices_unchanged':{},'event_count_histograms':True,'residual_convention':'reconstructed minus target, no display offsets','pages_per_slice':5,'pages_per_foil':30}
metrics=[]
with uproot.open(work/'SHMS_run25521/balanced/Optics_25521_-1_fit_tree_gmm.root') as f:
 reference=f['TFit'].arrays(library='np')
for case,method in [('unweighted','Unweighted legacy fit'),('weighted','Supplied weights')]:
 matrix=out/case/'matrices'/f'nps_shms_newfit_25521_{case}.dat'; before=hashlib.sha256(matrix.read_bytes()).hexdigest()
 for side in ['old','new']:
  inputpath=work/'SHMS_run25521'/f'{case}_{side}.root'
  with uproot.open(inputpath) as f: data=f['TFit'].arrays(library='np')
  assert len(data['delta'])==sel['fit_events']
  for key in ['xfp','xpfp','yfp','ypfp','delta','xtar','xtarT','ytarT','xptarT','yptarT','ztarT','xsT','ysT']:
   # xtarT is not separately carried in the plotting copy; xtar is identical.
   assert np.array_equal(data.get(key,data['xtar']),reference[key]),key
  for nf,z in enumerate(zs):
   folder=out/case/'plots'/side/foilnames[nf]; folder.mkdir(parents=True,exist_ok=True)
   combined=PdfWriter()
   for nd in range(6):
    low=max(-15,edges[nd]); high=min(30,edges[nd+1]); mask=(data['ztarT']==z)&(data['delta']>=edges[nd])&(data['delta']<edges[nd+1]); a={k:v[mask] for k,v in data.items()}; n=len(a['delta'])
    assert n==counts[nf,nd],(nf,nd,n,counts[nf,nd])
    residuals=[1000*(a['xptar']-a['xptarT']),a['ytar']-a['ytarT'],1000*(a['yptar']-a['yptarT'])]
    truths=[a['xptarT'],a['ytarT'],a['yptarT']]
    columns=[np.rint(a['xsT']/2.5).astype(int),np.rint(a['ysT']/1.64).astype(int),np.rint(a['ysT']/1.64).astype(int)]
    relation='<' if nd==0 else '<='
    title=f'{method} | {side.upper()} matrix | foil {nf}, z={z:+d} cm | {low:g} {relation} delta < {high:g}% | N={n}'
    path=folder/(slices[nd]+'.pdf'); keep=[]
    def canvas(subtitle,nx,ny):
     c=ROOT.TCanvas(f'canvas_{len(keep)}','foil/slice diagnostics',1400,1000); keep.append(c)
     h=ROOT.TPaveText(.01,.94,.99,.995,'NDC'); h.SetFillStyle(0);h.SetBorderSize(0);h.SetTextSize(.021);h.AddText(title);h.AddText(subtitle);h.Draw();keep.append(h)
     p=ROOT.TPad('body','',0,.025,1,.935);p.Draw();p.cd();p.Divide(nx,ny);keep.append(p)
     return c,p
    def h1(values,axis,titlex,span=None):
     rr=ranges[axis] if span is None else span
     h=ROOT.TH1D(f'h{len(keep)}',titlex,100,-rr,rr);h.SetDirectory(0);keep.append(h)
     for v in values:h.Fill(float(v))
     h.SetLineColor(ROOT.kBlue+1);h.SetLineWidth(2);h.GetXaxis().SetTitle(f'{axes[axis]} residual ({units[axis]})');h.GetYaxis().SetTitle('Events');h.Draw('hist')
     overflow=int(np.sum((values < -rr)|(values>=rr)))
     text=ROOT.TPaveText(.45,.68,.86,.89,'NDC');text.SetFillStyle(0);text.SetBorderSize(0);text.SetTextSize(.031)
     text.AddText(f'N={len(values)}, outside range={overflow}')
     if len(values):text.AddText(f'mean={np.mean(values):.4g}, RMS={np.std(values):.4g}');text.AddText(f'RMSE={np.sqrt(np.mean(values**2)):.4g}')
     else:text.AddText('EMPTY: no events')
     text.Draw();keep.append(text)
    def h2(x,y,name,xlabel,ylabel,xrange,yrange):
     h=ROOT.TH2D(f'h{len(keep)}',name,70,*xrange,70,*yrange);h.SetDirectory(0);keep.append(h)
     for u,v in zip(x,y):h.Fill(float(u),float(v))
     h.GetXaxis().SetTitle(xlabel);h.GetYaxis().SetTitle(ylabel);h.Draw('colz');return h
    c,p=canvas('Distributions and residual correlations; raw residuals, no display shifts; statistics include tails',3,2)
    for j in range(3):
     p.cd(j+1);h1(residuals[j],j,axes[j]+' residual')
     p.cd(j+4);h2(truths[j],residuals[j],axes[j]+' residual versus target',axes[j]+' target ('+('cm' if j==1 else 'slope')+')',f'Residual ({units[j]})',(-7,7) if j==1 else (-.065,.065),(-ranges[j],ranges[j]))
    c.Print(str(path)+'(')
    for j in range(3):
     c,p=canvas(f'{axes[j]} residual distributions by '+('x' if j==0 else 'y')+' sieve column; empty columns shown explicitly',4,3)
     for k,col in enumerate(range(-5,6)):
      p.cd(k+1);h1(residuals[j][columns[j]==col],j,f'Sieve column {col:+d} ({col*(2.5 if j==0 else 1.64):g} cm)')
     c.Print(str(path))
    c,p=canvas('Sieve reconstruction and residuals versus delta; fixed geometric xtar, not an iterative replay',2,2)
    d=a['delta'];hb=-.0398*d+.000398*d*d
    xr=a['xtar']+253*a['xptar']; yr=a['ytar']+253*a['yptar']+hb
    p.cd(1);h2(xr,yr,'Reconstructed sieve; red crosses = occupied label targets','x sieve (cm)','y sieve (cm)',(-16,16),(-11,11))
    unique=np.unique(np.column_stack([a['xsT'],a['ysT']]),axis=0)
    graph=ROOT.TGraph(len(unique),np.ascontiguousarray(unique[:,0]),np.ascontiguousarray(unique[:,1]));graph.SetMarkerStyle(5);graph.SetMarkerColor(ROOT.kRed);graph.SetMarkerSize(1);graph.Draw('P SAME');keep.append(graph)
    for j in range(3):
     p.cd(j+2);h2(d,residuals[j],axes[j]+' residual versus delta','delta (%)',f'Residual ({units[j]})',(low,high),(-ranges[j],ranges[j]))
    c.Print(str(path)+')')
    r=PdfReader(path);assert len(r.pages)==5
    combined.append(r,outline_item=f'Foil {nf}, z={z:+d} cm, delta [{low:g},{high:g})%, N={n}')
    rec={'case':case,'side':side,'foil_id':nf,'z_cm':z,'delta_low':low,'delta_low_inclusive':nd!=0,'delta_high_exclusive':high,'events':n,'pdf':str(path.relative_to(out)),'pages':5}
    report['case_side_foil_slices'].append(rec)
    for j in range(3): metrics.append(dict(case=case,side=side,foil_id=nf,z_cm=z,delta_low=low,delta_high=high,events=n,axis=axes[j],unit=units[j],mean=float(np.mean(residuals[j])),rms=float(np.std(residuals[j])),rmse=float(np.sqrt(np.mean(residuals[j]**2))),outside_display_range=int(np.sum(abs(residuals[j])>=ranges[j]))))
    print(case,side,'foil',nf,'slice',nd,'N',n,flush=True)
    ROOT.gROOT.GetListOfCanvases().Delete()
   with (folder/'all_delta_slices.pdf').open('wb') as stream:combined.write(stream)
   combined.close()
 report['matrices_unchanged'][case]=hashlib.sha256(matrix.read_bytes()).hexdigest()==before;assert report['matrices_unchanged'][case]
# Verify each case/side has all 18 unique populated slices and totals match the fit.
for case in ['unweighted','weighted']:
 for side in ['old','new']:
  records=[r for r in report['case_side_foil_slices'] if r['case']==case and r['side']==side]
  assert len(records)==18 and sum(r['events'] for r in records)==sel['fit_events']
  assert all(sum(r['events'] for r in records if r['foil_id']==f)==24396 for f in range(3))
with (out/'foil_slice_metrics.csv').open('w') as stream:
 writer=csv.DictWriter(stream,fieldnames=list(metrics[0]),lineterminator='\n');writer.writeheader();writer.writerows(metrics)
(out/'foil_slice_validation.json').write_text(json.dumps(report,indent=2)+'\n')
