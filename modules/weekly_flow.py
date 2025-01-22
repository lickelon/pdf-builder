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

# def get_problem_dict(path):
#     folder_path = Path(path)
#     pdf_files = folder_path.glob('**/*.pdf')

#     problem_dict = dict()
#     for pdf_file in pdf_files:
#         pdf_src_path = str(pdf_file)
#         item_code = pdf_file.stem
#         problem_dict[item_code] = pdf_src_path
#     return problem_dict

# def get_problem_list(file_path):
#     with open(file_path, 'r') as file:
#         return file.readline().split(',')

# def get_item_json():
#     with open("input/weekly_item.json", encoding='UTF8') as file:
#         item_data = json.load(file)
#     return item_data

# def get_unit_title(unit_code):
#     with open("resources/topic.json", encoding='UTF8') as file:
#         topic_data = json.load(file)
#     return topic_data[unit_code]

# def append_new_list_to_paragraph(paragraph: ParagraphOverlayObject, num, overlayer, base):
#     if num % 2 == 0:
#         overlayer.add_page(base)
#         paragraph_list = ListOverlayObject(num//2, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(34), 0), Ratio.mm_to_px(304), 0)
#         paragraph.add_paragraph_list(paragraph_list=paragraph_list)
#         #append left area
#         pass
#     else:
#         #append right area on last page
#         paragraph_list = ListOverlayObject(num//2, Coord(Ratio.mm_to_px(138.5), Ratio.mm_to_px(34), 0), Ratio.mm_to_px(304), 0)
#         paragraph.add_paragraph_list(paragraph_list=paragraph_list)
#         pass
#     pass

# def add_child_to_paragraph(paragraph: ParagraphOverlayObject, child: OverlayObject, num, overlayer, base):
#     if paragraph.add_child(child): return num
#     append_new_list_to_paragraph(paragraph, num, overlayer, base)
#     paragraph.add_child(child)
#     return num+1

# def get_item_list_on_paragraph(items):
#     item_list = [[] for i in range(13)]
#     for item in items:
#         if item['FC_para'] > 1:
#             item_list[item['FC_para']//10].append((item['FC_para']%10,item['item_code']))
    
#     new_item_list = []
#     for para in item_list:
#         if len(para) != 0:
#             new_item_list.append(para)

#     return new_item_list

# def set_page(overlayer, resources_pdf, resources_doc, page_amount):
#     if page_amount == 1:
#         overlayer.add_page(Component(resources_pdf, 2, resources_doc.load_page(2).rect))
#         overlayer.add_page(Component(resources_pdf, 4, resources_doc.load_page(4).rect))
#     elif page_amount == 2:
#         overlayer.add_page(Component(resources_pdf, 2, resources_doc.load_page(2).rect))
#         overlayer.add_page(Component(resources_pdf, 3, resources_doc.load_page(3).rect))
#     elif page_amount == 3:
#         overlayer.add_page(Component(resources_pdf, 2, resources_doc.load_page(2).rect))
#         overlayer.add_page(Component(resources_pdf, 3, resources_doc.load_page(3).rect))
#         overlayer.add_page(Component(resources_pdf, 2, resources_doc.load_page(2).rect))
#         overlayer.add_page(Component(resources_pdf, 4, resources_doc.load_page(4).rect))
#     elif page_amount == 4:
#         overlayer.add_page(Component(resources_pdf, 2, resources_doc.load_page(2).rect))
#         overlayer.add_page(Component(resources_pdf, 3, resources_doc.load_page(3).rect))
#         overlayer.add_page(Component(resources_pdf, 2, resources_doc.load_page(2).rect))
#         overlayer.add_page(Component(resources_pdf, 3, resources_doc.load_page(3).rect))

# def set_lists(page_num, k):
#     paragraphs_base = ShapeOverlayObject(page_num, Coord(Ratio.mm_to_px(0), Ratio.mm_to_px(35), 0), Rect(0,0,Ratio.mm_to_px(262),Ratio.mm_to_px(k+22)), (0,0,0,0.05))
#     paragraphs_base.add_child(ListOverlayObject(page_num, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(11), 1), Ratio.mm_to_px(k), 1))
#     paragraphs_base.add_child(ListOverlayObject(page_num, Coord(Ratio.mm_to_px(97.25), Ratio.mm_to_px(11), 1), Ratio.mm_to_px(k), 1))
#     paragraphs_base.add_child(ListOverlayObject(page_num, Coord(Ratio.mm_to_px(174.5), Ratio.mm_to_px(11), 1), Ratio.mm_to_px(k), 1))
#     return paragraphs_base

# def get_lists_on_page(page_amount):
#     lists = []
#     if page_amount == 1:
#         lists.append(set_lists(0, 334))
#     elif page_amount == 2:
#         lists.append(set_lists(0, 220))
#         lists.append(set_lists(1, 220))
#     elif page_amount == 3:
#         lists.append(set_lists(0, 220))
#         lists.append(set_lists(1, 220))
#         lists.append(set_lists(2, 334))
#     elif page_amount == 4:
#         lists.append(set_lists(0, 220))
#         lists.append(set_lists(1, 220))
#         lists.append(set_lists(2, 220))
#         lists.append(set_lists(3, 220))
#     return lists

# def build():
#     new_doc = fitz.open()

#     item_data = get_item_json()
#     items = item_data['items']

#     resources_pdf = "resources/weekly_main_resources.pdf"
#     resources_doc = fitz.open(resources_pdf)

#     overlayer = Overlayer(new_doc)

#     item_lists = get_item_list_on_paragraph(items)
#     page_amount = (len(item_lists)+1)//3
#     set_page(overlayer, resources_pdf, resources_doc, page_amount)

#     para_lists = get_lists_on_page(page_amount)
#     for i in range(len(item_lists)):
#         for item in item_lists[i]:
#             item_pdf = f"KiceDB/{item[1][2:5]}/{item[1]}/{item[1]}_original.pdf"
#             with fitz.open(item_pdf) as file:
#                 page = file.load_page(0)
#                 rect = page.rect
#                 component = Component(item_pdf, 0, page.rect)
#             oo = ResizedComponentOverlayObject(i//3, Coord(Ratio.mm_to_px(0.175),Ratio.mm_to_px(0.175),0), component, 0.6)

#             problem = ShapeOverlayObject(i//3, Coord(0,0,0), Rect(0,0,rect.width*0.6+Ratio.mm_to_px(0.35),rect.height*0.6+Ratio.mm_to_px(0.35)), (0.75, 0.4, 0, 0))
#             problem.add_child(ShapeOverlayObject(i//3, Coord(Ratio.mm_to_px(0.175),Ratio.mm_to_px(0.175),1), Rect(0,0,rect.width*0.6,rect.height*0.6), (0, 0, 0, 0)))
#             problem.child[0].add_child(oo)
#             para_lists[i//3].child[i%3].add_child(problem)
    
#     for para in para_lists:
#         height = 0
#         for oo in para.child:
#             height = max(height, oo.get_height() + (len(oo.child)-1)*Ratio.mm_to_px(10))
#         for oo in para.child:
#             oo.set_height(height)
#         para.rect.y1 = height + Ratio.mm_to_px(22)
#         print(height)

#     if len(para_lists) > 1:
#         height = max(para_lists[0].child[0].height, para_lists[1].child[0].height)
#         for oo in para_lists[0].child:
#             oo.set_height(height)
#         for oo in para_lists[1].child:
#             oo.set_height(height)
#         para_lists[0].rect.y1 = height + Ratio.mm_to_px(22)
#         para_lists[1].rect.y1 = height + Ratio.mm_to_px(22)

#     if len(para_lists) == 4:
#         height = max(para_lists[2].child[0].height, para_lists[3].child[0].height)
#         for oo in para_lists[2].child:
#             oo.set_height(height)
#         for oo in para_lists[3].child:
#             oo.set_height(height)
#         para_lists[2].rect.y1 = height + Ratio.mm_to_px(22)
#         para_lists[3].rect.y1 = height + Ratio.mm_to_px(22)

#     for para in para_lists:
#         para.overlay(overlayer, Coord(0,Ratio.mm_to_px(35),0))

#     #TODO 나머지 잡다한 것

#     new_doc.save("output/weekly_flow_test.pdf")
#     resources_doc.close()


class FlowBuilder:
    def __init__(self, topic, items):
        self.topic = topic
        self.items = items

    def get_component_on_resources(self, page_num):
        return Component(self.resources_pdf, page_num, self.resources_doc.load_page(page_num).rect)
    
    def get_unit_title(self):
        with open("resources/topic.json", encoding='UTF8') as file:
            topic_data = json.load(file)
        return topic_data[self.topic]
    
    def set_page(self):
        if self.page_amount == 1:
            self.overlayer.add_page(self.get_component_on_resources(2))
            self.overlayer.add_page(self.get_component_on_resources(4))
        elif self.page_amount == 2:
            self.overlayer.add_page(self.get_component_on_resources(2))
            self.overlayer.add_page(self.get_component_on_resources(3))
        elif self.page_amount == 3:
            self.overlayer.add_page(self.get_component_on_resources(2))
            self.overlayer.add_page(self.get_component_on_resources(3))
            self.overlayer.add_page(self.get_component_on_resources(2))
            self.overlayer.add_page(self.get_component_on_resources(4))
        elif self.page_amount == 4:
            self.overlayer.add_page(self.get_component_on_resources(2))
            self.overlayer.add_page(self.get_component_on_resources(3))
            self.overlayer.add_page(self.get_component_on_resources(2))
            self.overlayer.add_page(self.get_component_on_resources(3))

    def set_lists(self, page_num, k):
        paragraphs_base = ShapeOverlayObject(page_num, Coord(Ratio.mm_to_px(0), Ratio.mm_to_px(35), 0), Rect(0,0,Ratio.mm_to_px(262),Ratio.mm_to_px(k+22)), (0,0,0,0.05))
        paragraphs_base.add_child(ListOverlayObject(page_num, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(11), 1), Ratio.mm_to_px(k), 1))
        paragraphs_base.add_child(ListOverlayObject(page_num, Coord(Ratio.mm_to_px(97.25), Ratio.mm_to_px(11), 1), Ratio.mm_to_px(k), 1))
        paragraphs_base.add_child(ListOverlayObject(page_num, Coord(Ratio.mm_to_px(174.5), Ratio.mm_to_px(11), 1), Ratio.mm_to_px(k), 1))
        return paragraphs_base
    
    def get_lists_on_page(self):
        lists = []
        if self.page_amount == 1:
            lists.append(self.set_lists(0, 334))
        elif self.page_amount == 2:
            lists.append(self.set_lists(0, 220))
            lists.append(self.set_lists(1, 220))
        elif self.page_amount == 3:
            lists.append(self.set_lists(0, 220))
            lists.append(self.set_lists(1, 220))
            lists.append(self.set_lists(2, 334))
        elif self.page_amount == 4:
            lists.append(self.set_lists(0, 220))
            lists.append(self.set_lists(1, 220))
            lists.append(self.set_lists(2, 220))
            lists.append(self.set_lists(3, 220))
        return lists
    
    def get_item_list_on_paragraph(self):
        item_list = [[] for i in range(13)]
        for item in self.items:
            if item['FC_para'] is not None and item['FC_para'] > 1:
                item_list[item['FC_para']//10].append((item['FC_para']%10,item['item_code']))
        
        self.item_lists = []
        for para in item_list:
            if len(para) != 0:
                self.item_lists.append(para)
    
    def build(self):
        new_doc = fitz.open()

        self.resources_pdf = "resources/weekly_main_resources.pdf"
        self.resources_doc = fitz.open(self.resources_pdf)
        self.overlayer = Overlayer(new_doc)

        self.get_item_list_on_paragraph()
        self.page_amount = (len(self.item_lists)+1)//3
        self.set_page()

        para_lists = self.get_lists_on_page()
        for i in range(len(self.item_lists)):
            for item in self.item_lists[i]:
                item_pdf = f"KiceDB/{item[1][2:5]}/{item[1]}/{item[1]}_caption.pdf"
                with fitz.open(item_pdf) as file:
                    page = file.load_page(0)
                    rect = page.rect
                    component = Component(item_pdf, 0, page.rect)
                oo = ResizedComponentOverlayObject(i//3, Coord(Ratio.mm_to_px(0.175),Ratio.mm_to_px(0.175),0), component, 0.6)

                problem = ShapeOverlayObject(i//3, Coord(0,0,0), Rect(0,0,rect.width*0.6+Ratio.mm_to_px(0.35),rect.height*0.6+Ratio.mm_to_px(0.35)), (0.75, 0.4, 0, 0))
                problem.add_child(ShapeOverlayObject(i//3, Coord(Ratio.mm_to_px(0.175),Ratio.mm_to_px(0.175),1), Rect(0,0,rect.width*0.6,rect.height*0.6), (0, 0, 0, 0)))
                problem.child[0].add_child(oo)
                para_lists[i//3].child[i%3].add_child(problem)
        
        for para in para_lists:
            height = 0
            for oo in para.child:
                height = max(height, oo.get_height() + (len(oo.child)-1)*Ratio.mm_to_px(10))
            for oo in para.child:
                oo.set_height(height)
            para.rect.y1 = height + Ratio.mm_to_px(22)
            print(height)

        if len(para_lists) > 1:
            height = max(para_lists[0].child[0].height, para_lists[1].child[0].height)
            for oo in para_lists[0].child:
                oo.set_height(height)
            for oo in para_lists[1].child:
                oo.set_height(height)
            para_lists[0].rect.y1 = height + Ratio.mm_to_px(22)
            para_lists[1].rect.y1 = height + Ratio.mm_to_px(22)

        if len(para_lists) == 4:
            height = max(para_lists[2].child[0].height, para_lists[3].child[0].height)
            for oo in para_lists[2].child:
                oo.set_height(height)
            for oo in para_lists[3].child:
                oo.set_height(height)
            para_lists[2].rect.y1 = height + Ratio.mm_to_px(22)
            para_lists[3].rect.y1 = height + Ratio.mm_to_px(22)

        for para in para_lists:
            para.overlay(self.overlayer, Coord(0,Ratio.mm_to_px(35),0))
            y = para.coord.y + para.rect.height
            so = ShapeOverlayObject(para.page_num, Coord(0, y, 0), Rect(0,0,Ratio.mm_to_px(262),Ratio.mm_to_px(2)), (205/255, 216/255, 238/255))
            so.overlay(self.overlayer, Coord(0, y, 0))

        if len(para_lists) % 2 == 0:
            piv = len(para_lists)
            y = para_lists[piv-2].coord.y + para_lists[piv-2].rect.height
            so = ShapeOverlayObject(piv-2, Coord(Ratio.mm_to_px(20), y + Ratio.mm_to_px(16.25), 0), Rect(0,0,Ratio.mm_to_px(222),Ratio.mm_to_px(330.75)-y), (243/255, 246/255, 251/255))
            so.overlay(self.overlayer, Coord(Ratio.mm_to_px(20), y + Ratio.mm_to_px(16.25), 0))
            so = ShapeOverlayObject(piv-1, Coord(Ratio.mm_to_px(20), y + Ratio.mm_to_px(16.25), 0), Rect(0,0,Ratio.mm_to_px(222),Ratio.mm_to_px(330.75)-y), (243/255, 246/255, 251/255))
            so.overlay(self.overlayer, Coord(Ratio.mm_to_px(20), y + Ratio.mm_to_px(16.25), 0))
            
            so = ShapeOverlayObject(piv-2, Coord(Ratio.mm_to_px(20), y + Ratio.mm_to_px(16.25), 0), Rect(0,0,Ratio.mm_to_px(222), Ratio.mm_to_px(0.5/2.835)), (0.75, 0.45, 0, 0))
            so.overlay(self.overlayer, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(347), 0))
            so = ShapeOverlayObject(piv-1, Coord(Ratio.mm_to_px(20), y + Ratio.mm_to_px(16.25), 0), Rect(0,0,Ratio.mm_to_px(222), Ratio.mm_to_px(0.5/2.835)), (0.75, 0.45, 0, 0))
            so.overlay(self.overlayer, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(347), 0))

            component = self.get_component_on_resources(5)
            co = ComponentOverlayObject(piv-2, Coord(Ratio.mm_to_px(20),y+Ratio.mm_to_px(12),0), component)
            co.overlay(self.overlayer, Coord(Ratio.mm_to_px(20),y+Ratio.mm_to_px(12),0))
            component = self.get_component_on_resources(6)
            co = ComponentOverlayObject(piv-1, Coord(Ratio.mm_to_px(20),y+Ratio.mm_to_px(12),0), component)
            co.overlay(self.overlayer, Coord(Ratio.mm_to_px(20),y+Ratio.mm_to_px(12),0))

        for i in range(len(para_lists))[::2]:
            to = TextOverlayObject(i, Coord(Ratio.mm_to_px(18), Ratio.mm_to_px(20), 0), "resources/fonts/Pretendard-Black.ttf", 32.5, self.get_unit_title(), (1, 1, 1), fitz.TEXT_ALIGN_LEFT)
            to.overlay(self.overlayer, Coord(Ratio.mm_to_px(18), Ratio.mm_to_px(20), 0))
        #TODO 나머지 잡다한 것

        #짝수페이지라면 메모 추가

        self.resources_doc.close()
        return new_doc