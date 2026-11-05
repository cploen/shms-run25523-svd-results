"""Add a method banner without changing the vector plot content."""
from pathlib import Path
import argparse,io
import fitz
from pypdf import PdfReader,PdfWriter

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directories',nargs='+',type=Path)
    p.add_argument('--label',required=True)
    args=p.parse_args()
    for folder in args.directories:
        for path in folder.glob('*.pdf'):
            with fitz.open(path) as existing:
                if args.label in existing[0].get_text(): continue
            reader=PdfReader(path);writer=PdfWriter()
            for page in reader.pages:
                page.transfer_rotation_to_content();writer.add_page(page)
            data=io.BytesIO();writer.write(data)
            native=fitz.open(stream=data.getvalue(),filetype='pdf');output=fitz.open()
            for page in native:
                rect=page.rect
                target=output.new_page(width=rect.width,height=rect.height+27)
                target.show_pdf_page(fitz.Rect(0,27,rect.width,rect.height+27),native,page.number)
                target.draw_rect(fitz.Rect(0,0,rect.width,27),color=None,fill=(.93,.95,.98))
                target.insert_text((10,18),args.label,fontname='helv',fontsize=8,color=(.08,.15,.25))
            temp=path.with_suffix('.labeled.pdf');output.save(temp,garbage=4,deflate=True)
            output.close();native.close();temp.replace(path)
            print(path)

if __name__=='__main__': main()
