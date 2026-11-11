"""Delta (vertical, percent) versus fitted ytar (horizontal, cm), event counts."""
from pathlib import Path
import sys,json
import numpy as np,uproot,ROOT
repo=Path(__file__).resolve().parents[2];out=repo/'run25521';work=Path(sys.argv[1])
ROOT.gROOT.SetBatch(True);ROOT.gStyle.SetOptStat(0);ROOT.gStyle.SetPalette(ROOT.kBird)
ROOT.gStyle.SetPadLeftMargin(.12);ROOT.gStyle.SetPadRightMargin(.15)
ROOT.gStyle.SetTitleFontSize(.045)
report={'horizontal_axis':'new-matrix reconstructed ytar (cm)','vertical_axis':'experimental reconstructed delta (percent), unchanged by angular fit','event_count_histograms':True,'logarithmic_color':True,'selection':'same 73188 fitted events, 24396 per foil','new_full_replay':False,'cases':{}}
arrays={}
for case in ['unweighted','weighted']:
 with uproot.open(work/'SHMS_run25521'/f'{case}_new.root') as f:arrays[case]=f['TFit'].arrays(['ytar','delta','ztarT'],library='np')
assert np.array_equal(arrays['unweighted']['delta'],arrays['weighted']['delta'])
assert np.array_equal(arrays['unweighted']['ztarT'],arrays['weighted']['ztarT'])
allhist={};keep=[]
for case in arrays:
 a=arrays[case];hist=[]
 for z in [None,10,0,-10]:
  mask=np.ones(len(a['ytar']),bool) if z is None else a['ztarT']==z
  h=ROOT.TH2D(f'{case}_{"all" if z is None else str(z)}','',180,-5,5,148,-15,22);h.SetDirectory(0)
  for x,y in zip(a['ytar'][mask],a['delta'][mask]):h.Fill(float(x),float(y))
  assert int(h.GetEntries())==(73188 if z is None else 24396)
  assert h.Integral()==h.GetEntries() # no events hidden outside plotted ranges
  hist.append(h);keep.append(h)
 allhist[case]=hist
maxcolor=max(h.GetMaximum() for hist in allhist.values() for h in hist)
for case,label in [('unweighted','Unweighted legacy fit'),('weighted','Supplied weights')]:
 dest=out/case/'plots/new';hist=allhist[case]
 c=ROOT.TCanvas('delta_'+case,'Delta versus ytar',1500,1100);c.Divide(2,2)
 for k,(h,z) in enumerate(zip(hist,[None,10,0,-10])):
  c.cd(k+1);ROOT.gPad.SetLogz();h.SetMinimum(1);h.SetMaximum(maxcolor)
  title='All three foils' if z is None else f'Foil {k-1}: z={z:+d} cm'
  h.SetTitle(f'{label} - {title}, N={int(h.GetEntries())};New-matrix ytar (cm);Delta (%)')
  h.GetZaxis().SetTitle('Events / bin');h.Draw('COLZ')
 c.Print(str(dest/'25521_new_delta_vs_ytar.pdf'));c.Print(str(dest/'25521_new_delta_vs_ytar.png'))
 f=ROOT.TFile(str(dest/'25521_new_delta_vs_ytar.root'),'RECREATE')
 for h in hist:h.Write()
 c.Write('delta_vs_ytar');f.Close()
 report['cases'][case]={'entries':[int(h.GetEntries()) for h in hist],'plotted_ranges':{'ytar_cm':[-5,5],'delta_percent':[-15,22]},'all_events_within_display':True,'common_color_maximum':maxcolor,'weighting':'event counts, no histogram weight'}
(out/'delta_vs_ytar_validation.json').write_text(json.dumps(report,indent=2)+'\n')
