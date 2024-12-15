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

def get_sol_type_dict():
    sol_type_dict = {
        "HA" : 5,
        "HB" : 6,
        "HC" : 7,
        "HD" : 8,
        "HE" : 9,
        "NA" : 10,
        "NB" : 11,
        "NC" : 12,
        "ND" : 13,
        "NE" : 14,
        "EA" : 15,
        "EB" : 16,
        "EC" : 17,
        "arrow" : 18,
        "clip" : 19,
        "check" : 20,
        "exc_mark" : 21,
    }
    return sol_type_dict

def append_new_list_to_paragraph(paragraph: ParagraphOverlayObject, num, overlayer, base):
    if num % 2 == 0:
        overlayer.add_page(base)
        paragraph_list = ListOverlayObject(num//2, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(34), 0), Ratio.mm_to_px(304), 0)
        paragraph.add_paragraph_list(paragraph_list=paragraph_list)
        #append left area
        pass
    else:
        #append right area on last page
        paragraph_list = ListOverlayObject(num//2, Coord(Ratio.mm_to_px(138.5), Ratio.mm_to_px(34), 0), Ratio.mm_to_px(304), 0)
        paragraph.add_paragraph_list(paragraph_list=paragraph_list)
        pass
    pass

def add_child_to_paragraph(paragraph: ParagraphOverlayObject, child: OverlayObject, num, overlayer, base):
    if paragraph.add_child(child): return num
    append_new_list_to_paragraph(paragraph, num, overlayer, base)
    paragraph.add_child(child)
    return num+1

def get_unit_title(unit_code):
    with open("resources/topic.json", encoding='UTF8') as file:
        topic_data = json.load(file)
    return topic_data[unit_code]

def bake_unit_cover(resources_pdf, resources_doc, unit_code, num):
    component = Component(resources_pdf, 2, resources_doc.load_page(2).rect, ComponentType.a)
    unit_cover = AreaOverlayObject(0, Coord(0,0,0), Ratio.mm_to_px(24))
    unit_cover.add_child(ComponentOverlayObject(0, Coord(0,0,0), component))
    unit_cover.add_child(TextOverlayObject(0, Coord(Ratio.mm_to_px(7.5), Ratio.mm_to_px(10), 1), "resources/fonts/Cafe24Ohsquare-v2.0.ttf", 25, f"{num}", (1,1,1), fitz.TEXT_ALIGN_CENTER))
    unit_cover.add_child(TextOverlayObject(0, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(10), 1), "resources/fonts/Pretendard-SemiBold.ttf", 16.5, f"{get_unit_title(unit_code)}", (0,0,0), fitz.TEXT_ALIGN_LEFT))

    return unit_cover

def bake_problem_title(num, answer):
    problem_title = AreaOverlayObject(0, Coord(0,0,0), Ratio.mm_to_px(7))
    problem_title.add_child(TextOverlayObject(0, Coord(Ratio.mm_to_px(1), Ratio.mm_to_px(5.5), 1), "resources/fonts/Montserrat-Bold.ttf", 17, f"{num:02d}", (0.75, 0.4, 0, 0), fitz.TEXT_ALIGN_LEFT))
    problem_title.add_child(TextOverlayObject(0, Coord(Ratio.mm_to_px(12), Ratio.mm_to_px(5.5), 1), "resources/fonts/Pretendard-Bold.ttf", 11, "정답", (0.75, 0.4, 0, 0), fitz.TEXT_ALIGN_LEFT))
    problem_title.add_child(TextOverlayObject(0, Coord(Ratio.mm_to_px(19.5), Ratio.mm_to_px(5.5), 1), "resources/fonts/NanumSquareB.ttf", 11, f"{answer}", (0.75, 0.4, 0, 0), fitz.TEXT_ALIGN_LEFT))

    return problem_title

def bake_solutions(resources_pdf, resources_doc, commentary_data, item_pdf, solutions_info, sTF):
    solutions = []
    for solution_info in solutions_info:
        if commentary_data[solution_info.hexcode] == "answer":
            continue
        solution_object = AreaOverlayObject(0, Coord(0,0,0), 0)
        solution_component = Component(item_pdf, 0, solution_info.rect)
        res_page_num = get_sol_type_dict()[commentary_data[solution_info.hexcode]]
        type_component = Component(resources_pdf, res_page_num, resources_doc.load_page(res_page_num).rect)
        OX_component = None
        if sTF[solution_info.hexcode] == 1:
            OX_component = Component(resources_pdf, 3, resources_doc.load_page(3).rect)
        if sTF[solution_info.hexcode] == 0:
            OX_component = Component(resources_pdf, 4, resources_doc.load_page(4).rect)
        if OX_component is not None:
            solution_object.add_child(ComponentOverlayObject(0, Coord(Ratio.mm_to_px(-1), Ratio.mm_to_px(0.5), 1), OX_component))

        solution_object.add_child(ComponentOverlayObject(0, Coord(Ratio.mm_to_px(-1), 0, 2), type_component))
        solution_object.add_child(ComponentOverlayObject(0, Coord(Ratio.mm_to_px(5.5), 0, 2), solution_component))
        solution_object.height = solution_info.rect.height

        solutions.append(solution_object)

    return solutions
            
def bake_problem(resources_pdf, resources_doc, commentary_data, item_pdf, problem_num):
    objects = []
    with fitz.open(item_pdf) as file:
        ic = ItemCropper()
        solutions_info = ic.get_solution_infos_from_file(file, 10)
        sTF = ic.get_TF_of_solutions_from_file(file, 10)
        answer = ic.get_answer_from_file(file)
        objects.append(bake_problem_title(problem_num, answer))
        objects += bake_solutions(resources_pdf, resources_doc, commentary_data, item_pdf, solutions_info, sTF)
    return objects

def add_page_num(overlayer):
    for num in range(1, overlayer.doc.page_count+1):
        print(num)
        if num % 2:
            page_num_object = TextOverlayObject(num-1, Coord(Ratio.mm_to_px(244), Ratio.mm_to_px(358.5), 4), "resources/fonts/Pretendard-Bold.ttf", 14, f"{num}", (0, 0, 0), fitz.TEXT_ALIGN_RIGHT)
        else:
            page_num_object = TextOverlayObject(num-1, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(358.5), 4), "resources/fonts/Pretendard-Bold.ttf", 14, f"{num}", (0, 0, 0), fitz.TEXT_ALIGN_LEFT)
        page_num_object.overlay(overlayer, num-1, page_num_object.coord)
            

def build():
    new_doc = fitz.open()

    #setup
    problem_dict = get_problem_dict("input\weekly_sol")
    problem_list = get_problem_list("input\weekly_sol\item_list.txt")
    sol_type_dict = get_sol_type_dict()

    with open("resources/commentary.json") as file:
        commentary_data = json.load(file)

    resources_pdf = "resources/weekly_sol_resources.pdf"
    resources_doc = fitz.open(resources_pdf)

    overlayer = Overlayer(new_doc)
    base = Component(resources_pdf, 1, resources_doc.load_page(1).rect, ComponentType.a)
    # overlayer.add_page(base)
    paragraph = ParagraphOverlayObject()
    # unit_cover = bake_unit_cover(resources_pdf, resources_doc, "leb", 1)
    # unit_cover.overlay(overlayer, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(34), 0))
    # problem_title = bake_problem_title(1, "②")
    # problem_title.overlay(overlayer, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(34+24), 0))
    # solutions = bake_solutions(resources_pdf, resources_doc, commentary_data, problem_dict[problem_list[0]])
    # solutions.overlay(overlayer, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(34+24+7), 0))
    paragraph_cnt = 0
    unit_num = 0
    problem_num = 0
    before_unit = '---'
    for problem in problem_list:
        problem_num += 1
        if before_unit != problem[2:5]:
            append_new_list_to_paragraph(paragraph, paragraph_cnt, overlayer, base)
            paragraph_cnt += 1
            unit_num += 1
            unit_cover = bake_unit_cover(resources_pdf, resources_doc, problem[2:5], unit_num)
            paragraph_cnt = add_child_to_paragraph(paragraph, unit_cover, paragraph_cnt, overlayer, base)
        before_unit = problem[2:5]
        problem_objects = bake_problem(resources_pdf, resources_doc, commentary_data, problem_dict[problem], problem_num)
        for problem_object in problem_objects:
            paragraph_cnt = add_child_to_paragraph(paragraph, problem_object, paragraph_cnt, overlayer, base)
        
        paragraph.add_child(AreaOverlayObject(0, Coord(0,0,0), Ratio.mm_to_px(5)))

    paragraph.overlay(overlayer, 0, Coord(0,0,0))
    add_page_num(overlayer)
    new_doc.save("output/weekly_sol_test.pdf")
    resources_doc.close()
    pass