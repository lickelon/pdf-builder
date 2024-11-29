from modules.kice_cropper import KiceCropper
from pathlib import Path
if __name__ == '__main__':
    folder_path = Path('input')
    pdf_files = folder_path.glob('*.pdf')
    for pdf_file in pdf_files:
        pdf_src_path = str(pdf_file)
        item_code = pdf_file.stem
        print(item_code, end=' ')
        kc = KiceCropper(pdf_name=pdf_src_path)
        ret = kc.extract_problems(accuracy=10)
        print(f'extracted {ret} items')
        kc.save_original()
        kc.save_caption(caption_point=(2.5, 5), font_size=13)