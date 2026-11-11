"""Check expanded report coverage, headers, counts, pages and slice bookmarks."""
from pathlib import Path
import json
import fitz

def validate(out):
 p=out/'foil_slice_validation.json';v=json.loads(p.read_text());total=0
 for r in v['case_side_foil_slices']:
  with fitz.open(out/r['pdf']) as f:
   assert len(f)==5
   for page in f:
    text=page.get_text();assert f'foil {r["foil_id"]}, z={r["z_cm"]:+d} cm' in text
    assert f'N={r["events"]}' in text
    assert ('Supplied weights' if r['case']=='weighted' else 'Unweighted legacy fit') in text
   total+=len(f)
 combined=list(out.glob('*/plots/*/foil_*/all_delta_slices.pdf'));assert len(combined)==12
 for f in combined:
  with fitz.open(f) as d:
   assert len(d)==30 and sum(item[0]==1 for item in d.get_toc())==6;total+=len(d)
 assert len(v['case_side_foil_slices'])==72
 v.update(verified_slice_pdf_count=72,verified_combined_foil_pdf_count=12,verified_total_pages_including_combined_copies=total,all_page_foil_slice_count_method_headers_checked=True,combined_reports_have_six_slice_bookmarks=True)
 p.write_text(json.dumps(v,indent=2)+'\n')
 print('PASS: 72 slice PDFs, 12 combined foil PDFs,',total,'pages with foil/method/count headers')
if __name__=='__main__':validate(Path(__file__).resolve().parents[1])
