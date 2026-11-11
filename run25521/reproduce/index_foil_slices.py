"""Write navigation for explicit foil/slice ROOT diagnostic PDFs."""
import json
from pathlib import Path
out=Path(__file__).resolve().parents[1]; records=json.loads((out/'foil_slice_validation.json').read_text())['case_side_foil_slices']
zs=[10,0,-10]; folders=['foil_0_z_plus10','foil_1_z_0','foil_2_z_minus10']
lines=['# Run 25521 diagnostics: choose a foil, then a delta slice','',
'The original summary PDFs combine foils. **Use the links below for the actual foil-by-foil inspection.** Each foil report contains six delta slices, in increasing delta order; its PDF bookmarks select a slice. Each slice has five pages, described below.','',
'All views use the identical 73,188 fitted events (24,396 per foil), with matching old/new matrix inputs. There has been no refit or change to any matrix.','',
'## One report per foil','',
'| Method | Foil label / z | Old matrix (30 pages) | New matrix (30 pages) |','|---|---|---|---|']
for case,label in [('unweighted','Unweighted legacy fit'),('weighted','Supplied weights')]:
 for nf,z in enumerate(zs):
  links=[f'[{side.title()} foil {nf}]({case}/plots/{side}/{folders[nf]}/all_delta_slices.pdf)' for side in ['old','new']]
  lines.append(f'| {label} | {nf} / {z:+d} cm | '+ ' | '.join(links)+' |')
lines+=['','## What is on each slice’s five pages?','',
'1. Full xptar, ytar and yptar residual distributions, plus residual-versus-target 2D histograms. Counts, mean, RMS and RMSE are printed; tail counts outside the plotted range are explicit.',
'2. Xptar residual distributions for every x-sieve column (11 panels).',
'3. Yptar residual distributions for every y-sieve column (11 panels).',
'4. Ytar residual distributions for every y-sieve column (11 panels).',
'5. Reconstructed sieve pattern with occupied target holes marked, and each residual versus delta within that slice.','',
'Residuals are reconstructed minus geometric target; slopes are mrad and ytar is cm. These displays use raw residuals with **no historical ±0.035 cm plotting shifts**. All statistics include tails. Empty sieve columns are explicitly marked, and no Gaussian fit conceals a second population. Old/new use the same axis limits. These are event-count histograms for both methods, as in the legacy diagnostics.','',
'The new displays restore the distributions that were disabled or not written by the existing macros. They supplement the original legacy PDFs, which are preserved. The old/new comparison evaluates the respective matrix at the same geometric xtar; the reconstructed sieve is xtar+253*xptar and ytar+253*yptar+hb(delta). This is not a fresh iterative HCANA replay.','',
'## Direct links to individual delta slices','',
'The first slice retains the native strict lower cut delta > −15%; subsequent lower edges are inclusive. Upper edges are exclusive. Counts below are identical for both cases and both old/new views.']
for nf,z in enumerate(zs):
 lines += ['',f'### Foil {nf}: z = {z:+d} cm','', '| Delta (%) | Events | Unweighted old | Unweighted new | Supplied weights old | Supplied weights new |','|---|---:|---|---|---|---|']
 grouped=[r for r in records if r['case']=='unweighted' and r['side']=='old' and r['foil_id']==nf]
 for r in grouped:
  filename=Path(r['pdf']).name; links=[]
  for case in ['unweighted','weighted']:
   for side in ['old','new']:
    links.append(f'[PDF]({case}/plots/{side}/{folders[nf]}/{filename})')
  lower=r['delta_low']; high=r['delta_high_exclusive']; rel='<' if not r['delta_low_inclusive'] else '≤'
  lines.append(f'| {lower:g} {rel} δ < {high:g} | {r["events"]:,} | '+' | '.join(links)+' |')
lines+=['','[All foil/slice numerical metrics (CSV)](foil_slice_metrics.csv) · [Population and PDF validation](foil_slice_validation.json) · [Results and fitting details](README.md)','']
(out/'DIAGNOSTICS.md').write_text('\n'.join(lines))
