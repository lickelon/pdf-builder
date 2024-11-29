from modules.kice_cropper import KiceCropper
from pathlib import Path
if __name__ == '__main__':
    kc = KiceCropper()
    folder_path = Path('input')
    pdf_files = folder_path.glob('*.pdf')
    for pdf_file in pdf_files:
        pdf_src_path = str(pdf_file)
        item_code = pdf_file.stem
        print(item_code)
        kc.extract_problems_to_original(pdf_name=pdf_src_path, accuracy=10)