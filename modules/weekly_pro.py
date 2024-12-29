from modules.item_cropper import ItemCropper
from modules.overlayer import Overlayer
from pathlib import Path
import fitz
from utils.ratio import Ratio
from utils.pdf_utils import PdfUtils
from utils.solution_info import SolutionInfo
from utils.overlay_object import *
from utils.coord import Coord
import json

def get_problem_dict(path):
    folder_path = Path(path)
    pdf_files = folder_path.glob('**/*.pdf')

    problem_dict = dict()
    for pdf_file in pdf_files:
        pdf_src_path = str(pdf_file)
        item_code = pdf_file.stem
        problem_dict[item_code] = pdf_src_path
    return problem_dict

def get_problem_list(file_path):
    with open(file_path, 'r') as file:
        return file.readline().split(',')

def get_unit_title(unit_code):
    with open("resources/topic.json", encoding='UTF8') as file:
        topic_data = json.load(file)
    return topic_data[unit_code]

def append_new_list_to_paragraph(paragraph: ParagraphOverlayObject, num, overlayer, baseL, baseR):
    if num % 4 == 0:
        overlayer.add_page(baseL)
        #append left area to left page
        paragraph_list = ListOverlayObject(num//2, Coord(Ratio.mm_to_px(18), Ratio.mm_to_px(34), 0), Ratio.mm_to_px(303), 2)
        paragraph.add_paragraph_list(paragraph_list=paragraph_list)
        pass
    elif num % 4 == 1:
        #append right area to left page
        paragraph_list = ListOverlayObject(num//2, Coord(Ratio.mm_to_px(134), Ratio.mm_to_px(34), 0), Ratio.mm_to_px(303), 2)
        paragraph.add_paragraph_list(paragraph_list=paragraph_list)
        pass
    elif num % 4 == 2:
        overlayer.add_page(baseR)
        #append left area to right page
        paragraph_list = ListOverlayObject(num//2, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(34), 0), Ratio.mm_to_px(303), 2)
        paragraph.add_paragraph_list(paragraph_list=paragraph_list)
        pass
    elif num % 4 == 3:
        #append right area to right page
        paragraph_list = ListOverlayObject(num//2, Coord(Ratio.mm_to_px(136), Ratio.mm_to_px(34), 0), Ratio.mm_to_px(303), 2)
        paragraph.add_paragraph_list(paragraph_list=paragraph_list)
        pass
    pass

def add_child_to_paragraph(paragraph: ParagraphOverlayObject, child: OverlayObject, num, overlayer, baseL, baseR):
    if paragraph.add_child(child): return num
    append_new_list_to_paragraph(paragraph, num, overlayer, baseL, baseR)
    paragraph.add_child(child)
    return num+1

def add_unit_title(overlayer, page_num, title):
    if page_num % 2 == 0:
        unit_title_object = TextOverlayObject(page_num, Coord(Ratio.mm_to_px(18), Ratio.mm_to_px(14.5), 4), "resources/fonts/Pretendard-ExtraBold.ttf", 18, title, (0.75, 0.4, 0, 0), fitz.TEXT_ALIGN_LEFT)
    else:
        unit_title_object = TextOverlayObject(page_num, Coord(Ratio.mm_to_px(244), Ratio.mm_to_px(14.5), 4), "resources/fonts/Pretendard-ExtraBold.ttf", 18, title, (0.75, 0.4, 0, 0), fitz.TEXT_ALIGN_RIGHT)
    unit_title_object.overlay(overlayer, unit_title_object.coord)

def bake_problem_title(problem_num, source = None):
    problem_title = AreaOverlayObject(0, Coord(0,0,0), Ratio.mm_to_px(17))
    num_object = TextOverlayObject(0, Coord(Ratio.mm_to_px(0), Ratio.mm_to_px(13), 4), "resources/fonts/Pretendard-ExtraBold.ttf", 48, f"{problem_num}", (0.75, 0.4, 0, 0), fitz.TEXT_ALIGN_LEFT)
    problem_title.add_child(num_object)
    if source is not None:
        text = TextOverlayObject(0, Coord(0,0,0), "resources/fonts/Pretendard-Regular.ttf", 12, source, (1,1,1), fitz.TEXT_ALIGN_CENTER)
        text.get_width()
        box = ShapeOverlayObject(0, Coord(Ratio.mm_to_px(27), Ratio.mm_to_px(7.5), 2), Rect(0,0,Ratio.mm_to_px(4)+text.get_width(),Ratio.mm_to_px(5.5)), (0,0,0,0.5), 0.5/5.5)
        text.coord = Coord(box.rect.width/2, Ratio.mm_to_px(4.3), 3)
        box.add_child(text)
        problem_title.add_child(box)
        pass
    return problem_title
    pass
def code_to_text(problem_code):
    subject_text = {
        'P1' : '물1',
        'P2' : '물2',
        'C1' : '화1',
        'C2' : '화2',
        'B1' : '생1',
        'B2' : '생2',
        'E1' : '지1',
        'E2' : '지2',
    }
    month_text = {
        '06' : '6월',
        '09' : '9월',
        '11' : '대수능',
        '01' : '예비시행',
    }
    return f"20{problem_code[7:9]}학년도 {month_text[problem_code[9:11]]} {problem_code[11:13]}번 {subject_text[problem_code[0:2]]}"

def bake_problem(problem_dict, problem_code, problem_num):
    problem = AreaOverlayObject(0, Coord(0,0,0), 0)
    if problem_code[5:7] == 'KC':
        item_pdf = f"KiceDB/{problem_code[2:5]}/{problem_code}/{problem_code}_original.pdf"
        problem_title = bake_problem_title(problem_num, code_to_text(problem_code))
        problem.add_child(problem_title)
        problem.height += problem_title.get_height()
        with fitz.open(item_pdf) as file:
            page = file.load_page(0)
            component = Component(item_pdf, 0, page.rect)
            problem_object = ComponentOverlayObject(0, Coord(0, problem.height, 0), component)
            problem.add_child(problem_object)
            problem.height += problem_object.get_height()
        problem.height += Ratio.mm_to_px(10)
        pass
    else:
        problem_title = bake_problem_title(problem_num)
        problem.add_child(problem_title)
        problem.height += problem_title.get_height()
        item_pdf = problem_dict[problem_code]
        with fitz.open(item_pdf) as file:
            ic = ItemCropper()
            prect = ic.get_problem_rect_from_file(file, 10)
            component = Component(item_pdf, 0, prect)
            problem_object = ComponentOverlayObject(0, Coord(0, problem.height, 0), component)
            white_box = ShapeOverlayObject(0, Coord(0,0,0), Rect(0,0,Ratio.mm_to_px(2.5),Ratio.mm_to_px(5)), (1,1,1))
            problem_object.add_child(white_box)
            problem.add_child(problem_object)
            problem.height += problem_object.get_height()
        problem.height += Ratio.mm_to_px(10)
    return problem

def add_page_num(overlayer):
    for num in range(1, overlayer.doc.page_count+1):
        #print(num)
        num += 1
        if num % 2:
            page_num_object = TextOverlayObject(num-2, Coord(Ratio.mm_to_px(244), Ratio.mm_to_px(358.5), 4), "resources/fonts/Pretendard-Bold.ttf", 14, f"{num}", (0, 0, 0), fitz.TEXT_ALIGN_RIGHT)
        else:
            page_num_object = TextOverlayObject(num-2, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(358.5), 4), "resources/fonts/Pretendard-Bold.ttf", 14, f"{num}", (0, 0, 0), fitz.TEXT_ALIGN_LEFT)
        page_num_object.overlay(overlayer, page_num_object.coord)

def build():
    new_doc = fitz.open()

    #setup
    problem_dict = get_problem_dict("input\weekly2")
    problem_list = get_problem_list("input\weekly2\item_list.txt")

    resources_pdf = "resources/weekly_pro_resources.pdf"
    resources_doc = fitz.open(resources_pdf)

    overlayer = Overlayer(new_doc)
    baseL = Component(resources_pdf, 2, resources_doc.load_page(2).rect)
    baseR = Component(resources_pdf, 3, resources_doc.load_page(3).rect)
    baseM = Component(resources_pdf, 4, resources_doc.load_page(4).rect)

    paragraph = ParagraphOverlayObject()
    paragraph_cnt = 0
    problem_num = 0
    before_unit = '---'
    #problem_list.append('-----')
    for problem in problem_list:
        problem_num += 1
        if before_unit != problem[2:5]:
            #TODO add memo
            if overlayer.doc.page_count % 2:
                overlayer.add_page(baseM)
            if paragraph_cnt % 4 != 0:
                paragraph_cnt += 4 - paragraph_cnt % 4
            append_new_list_to_paragraph(paragraph, paragraph_cnt, overlayer, baseL, baseR)
            paragraph_cnt += 1
        if paragraph_cnt % 2 == 1:
            add_unit_title(overlayer, overlayer.doc.page_count-1, get_unit_title(problem[2:5]))
        before_unit = problem[2:5]
        problem_object = bake_problem(problem_dict, problem, problem_num)
        paragraph_cnt = add_child_to_paragraph(paragraph, problem_object, paragraph_cnt, overlayer, baseL, baseR)
        pass

    paragraph.overlay(overlayer, Coord(0,0,0))
    add_page_num(overlayer)
    new_doc.save("output/weekly_pro_test.pdf")
    resources_doc.close()
    pass