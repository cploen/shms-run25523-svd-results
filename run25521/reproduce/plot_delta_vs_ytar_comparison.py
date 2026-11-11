"""Matched before/after delta-versus-ytar ROOT displays; no fit or replay."""
from pathlib import Path
import sys,json
import numpy as np,uproot,ROOT
repo=Path(__file__).resolve().parents[2];out=repo/'run25521';work=Path(sys.argv[1])
ROOT.gROOT.SetBatch(True);ROOT.gStyle.SetOptStat(0);ROOT.gStyle.SetPalette(ROOT.kBird)
ROOT.gStyle.SetPadLeftMargin(.12);ROOT.gStyle.SetPadRightMargin(.15);ROOT.gStyle.SetTitleFontSize(.042)
arrays={};hist={};keep=[]
fields=['ytar','delta','ztarT','xfp','xpfp','yfp','ypfp','xtar','ytarT','xsT','ysT']
for case in ['unweighted','weighted']:
 for side in ['old','new']:
  with uproot.open(work/'SHMS_run25521'/f'{case}_{side}.root') as f:arrays[case,side]=f['TFit'].arrays(fields,library='np')
for key,a in arrays.items():
 for field in fields:
  if field!='ytar':assert np.array_equal(a[field],arrays['unweighted','old'][field]),(key,field)
 assert len(a['ytar'])==73188
xmin,xmax=-6.,6.;ymin,ymax=-15.,22.;nbx,nby=216,148
for (case,side),a in arrays.items():
 for k,z in enumerate([None,10,0,-10]):
  mask=np.ones(len(a['ytar']),bool) if z is None else a['ztarT']==z
  h=ROOT.TH2D(f'{case}_{side}_{k}','',nbx,xmin,xmax,nby,ymin,ymax);h.SetDirectory(0)
  for x,y in zip(a['ytar'][mask],a['delta'][mask]):h.Fill(float(x),float(y))
  assert int(h.GetEntries())==(73188 if z is None else 24396)
  assert h.Integral()==h.GetEntries()
  hist[case,side,k]=h;keep.append(h)
maxcolor=float(max(h.GetMaximum() for h in hist.values()))
report={'selection':'identical 73188 fitted events (24396 per foil), both methods, before and after','same_input_arrays_and_order_checked':True,'before':'starting matrix evaluated at geometric xtar','after':'emitted new fit matrix evaluated at the same geometric xtar','horizontal_axis':'reconstructed ytar (cm)','vertical_axis':'experimental reconstructed delta (%)','histogram_weighting':'event counts for both fits','color_scale':'common logarithmic scale across every panel and both cases','color_min':1,'color_max':maxcolor,'binning':[nbx,nby],'ranges':{'ytar_cm':[xmin,xmax],'delta_percent':[ymin,ymax]},'all_events_within_display':True,'full_HCANA_replay':False,'cases':{}}
def draw(case,side,k,label):
 h=hist[case,side,k];ROOT.gPad.SetLogz();h.SetMinimum(1);h.SetMaximum(maxcolor)
 foil='All foils' if k==0 else f'Foil {k-1}, z={[10,0,-10][k-1]:+d} cm'
 state='BEFORE: starting matrix' if side=='old' else 'AFTER: new fit'
 h.SetTitle(f'{label} | {state} | {foil}, N={int(h.GetEntries())};Reconstructed ytar (cm);Delta (%)')
 h.GetZaxis().SetTitle('Events / bin');h.Draw('COLZ')
for case,label in [('unweighted','Unweighted legacy fit'),('weighted','Supplied weights')]:
 dest=out/case/'plots/comparison';dest.mkdir(exist_ok=True)
 overview=ROOT.TCanvas('overview_'+case,'Before / after',1600,1900);overview.Divide(2,4)
 for k in range(4):
  for j,side in enumerate(['old','new']):overview.cd(2*k+j+1);draw(case,side,k,label)
 overview.Print(str(dest/'25521_delta_vs_ytar_before_after.png'))
 pdf=dest/'25521_delta_vs_ytar_before_after.pdf';pages=[]
 for k in range(4):
  c=ROOT.TCanvas(f'{case}_pair_{k}','Before / after',1600,700);c.Divide(2,1);keep.append(c)
  for j,side in enumerate(['old','new']):c.cd(j+1);draw(case,side,k,label)
  suffix='(' if k==0 else ')' if k==3 else ''
  c.Print(str(pdf)+suffix);pages.append(c)
 root=ROOT.TFile(str(dest/'25521_delta_vs_ytar_before_after.root'),'RECREATE')
 for (cc,side,k),h in hist.items():
  if cc==case:h.Write()
 overview.Write('overview')
 for k,c in enumerate(pages):c.Write('before_after_'+str(k))
 root.Close()
 report['cases'][case]={'before_entries':[int(hist[case,'old',k].GetEntries()) for k in range(4)],'after_entries':[int(hist[case,'new',k].GetEntries()) for k in range(4)],'pdf_pages':['all foils','foil 0: +10 cm','foil 1: 0 cm','foil 2: -10 cm']}
(out/'delta_vs_ytar_before_after_validation.json').write_text(json.dumps(report,indent=2)+'\n')
