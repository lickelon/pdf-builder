from modules.kice_cropper import KiceCropper
from modules.item_cropper import ItemCropper
from modules.overlayer import Overlayer
from pathlib import Path
import fitz
from utils.ratio import Ratio
from utils.pdf_utils import PdfUtils
from utils.solution_info import SolutionInfo
from utils.overlay_object import *
from utils.coord import Coord
def kc_test():
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

def ic_test():
    with fitz.open('input/E1lebKC211114.pdf') as file:
        ic = ItemCropper()
        #get problem
        ic.get_problem_rect_from_file(file, 10)
        #get solution
        ret = ic.get_solution_infos_from_file(file, 10)
        print(ic.get_TF_of_solutions_from_file(file, 10))
        print(ic.get_answer_from_file(file))

def o_test():
    new_doc = fitz.open()
    o = Overlayer(new_doc)
    o.add_page()
    o.text_overlay(0, Coord(Ratio.mm_to_px(148.5), 100, 0), "Eulyoo1945-Regular.ttf", 10, "\ntest text", (1,0,0), fitz.TEXT_ALIGN_CENTER)
    o.pdf_overlay(0, Coord(Ratio.mm_to_px(148), 90, 0), Component("input\TH_Problem_Test.pdf", 0, Rect(0,0,200,400), ComponentType.a))
    new_doc.save("output/overlayertest.pdf")

if __name__ == '__main__':
    from modules.weekly_sol import build
    build()
    pass