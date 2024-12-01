from modules.kice_cropper import KiceCropper
from pathlib import Path
import fitz
if __name__ == '__main__':
    folder_path = Path('input')
    pdf_files = folder_path.glob('*.pdf')

    new_doc = fitz.open()

    for pdf_file in pdf_files:
        pdf_src_path = str(pdf_file)
        item_code = pdf_file.stem
        print(item_code, end=' ')
        kc = KiceCropper(pdf_name=pdf_src_path)
        ret = kc.extract_problems(accuracy=10)
        print(f'extracted {ret} items')
        kc.save_original()
        kc.save_caption(caption_point=(2.5, 5), font_size=13)

        with fitz.open(pdf_src_path) as file:
            for info in kc.infos:
                new_page = new_doc.new_page(width=info.rect.width, height=info.rect.height)
                new_page.show_pdf_page(fitz.Rect(0,0,info.rect.width,info.rect.height), file, info.page_num, clip=info.rect)
        
    new_doc.save("output/total.pdf")