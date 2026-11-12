"""Standalone, unweighted delta counts for the shared fitted sample and each foil."""
from pathlib import Path
import sys,json,csv
import numpy as np,uproot,ROOT
repo=Path(__file__).resolve().parents[2];out=repo/'run25521';work=Path(sys.argv[1]);dest=out/'plots';dest.mkdir(exist_ok=True)
with uproot.open(work/'SHMS_run25521/balanced/Optics_25521_-1_fit_tree_gmm.root') as f:a=f['TFit'].arrays(['delta','ztarT'],library='np')
# Verify the displayed delta and foil arrays are shared by both new-fit inputs.
for case in ['unweighted','weighted']:
 with uproot.open(work/'SHMS_run25521'/f'{case}_new.root') as f:b=f['TFit'].arrays(['delta','ztarT'],library='np')
 for k in a:assert np.array_equal(a[k],b[k]),(case,k)
ROOT.gROOT.SetBatch(True);ROOT.gStyle.SetOptStat(0);ROOT.gStyle.SetTitleFontSize(.042)
ROOT.gStyle.SetPadLeftMargin(.12);ROOT.gStyle.SetPadBottomMargin(.12)
edges=np.arange(-15.,23.);hist=[];rows=[];report={'selection':'shared fitted events; no historical split selection','both_fits_identical_delta_arrays_and_order':True,'event_weights':'none; event counts','bin_width_percent':1,'range_percent':[-15,22],'panels':[]}
for k,z in enumerate([None,10,0,-10]):
 mask=np.ones(len(a['delta']),bool) if z is None else a['ztarT']==z
 values=a['delta'][mask];counts,_=np.histogram(values,bins=edges)
 assert int(counts.sum())==len(values)==(73188 if z is None else 24396)
 title='All three foils' if z is None else f'Foil {k-1}: z={z:+d} cm'
 h=ROOT.TH1D('delta_'+str(k),f'{title}, N={len(values)};Delta (%);Events / 1% bin',37,-15,22);h.SetDirectory(0)
 for value in values:h.Fill(float(value))
 assert h.Integral()==len(values)
 assert np.array_equal(np.array([h.GetBinContent(i+1) for i in range(37)]),counts)
 h.SetLineColor([ROOT.kBlack,ROOT.kBlue+1,ROOT.kRed+1,ROOT.kGreen+2][k]);h.SetLineWidth(2);h.SetMinimum(0)
 hist.append(h);report['panels'].append({'foil_id':None if z is None else k-1,'z_cm':z,'events':len(values),'minimum_delta':float(values.min()),'maximum_delta':float(values.max()),'counts':counts.tolist(),'underflow':0,'overflow':0})
 for i,count in enumerate(counts):rows.append({'population':'all' if z is None else f'foil_{k-1}','z_cm':'' if z is None else z,'delta_low_inclusive':float(edges[i]),'delta_high_exclusive':float(edges[i+1]),'events':int(count)})
assert np.array_equal(report['panels'][0]['counts'],np.sum([p['counts'] for p in report['panels'][1:]],axis=0))
c=ROOT.TCanvas('delta_histograms','Run 25521 delta counts',1400,1000);c.Divide(2,2)
foilmax=max(h.GetMaximum() for h in hist[1:])*1.15
for k,h in enumerate(hist):
 c.cd(k+1)
 if k:h.SetMaximum(foilmax)
 h.Draw('HIST')
 text=ROOT.TPaveText(.45,.76,.88,.87,'NDC');text.SetFillStyle(0);text.SetBorderSize(0);text.SetTextSize(.034);text.AddText('Shared fitted sample');text.AddText('Unweighted event counts');text.Draw()
 # Keep annotation objects alive through PDF/PNG output.
 if k==0:notes=[]
 notes.append(text)
c.Print(str(dest/'25521_delta_histograms.pdf'));c.Print(str(dest/'25521_delta_histograms.png'))
f=ROOT.TFile(str(dest/'25521_delta_histograms.root'),'RECREATE')
for h in hist:h.Write()
c.Write();f.Close()
with (dest/'25521_delta_histogram_counts.csv').open('w') as stream:
 writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
(out/'delta_histograms_validation.json').write_text(json.dumps(report,indent=2)+'\n')
