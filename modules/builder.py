import json
import fitz
from modules.weekly_flow import FlowBuilder
from modules.weekly_pro import ProblemBuilder
from modules.weekly_main import MainsolBuilder
from modules.weekly_ans import AnswerBuilder
from modules.weekly_sol import SolutionBuilder
from modules.overlayer import Overlayer
from utils.overlay_object import *
from utils.component import Component
from utils.ratio import Ratio

class Builder:
    def __init__(self, items):
        self.topics = []
        self.items = dict()
        for item in items:
            topic = item['topic_in_book']
            if topic in self.items:
                self.items[topic].append(item)
            else:
                self.topics.append(topic)
                self.items[topic] = []
                self.items[topic].append(item)

    def bake_topic_list(self, page_num, topic_num, fc_pages):
        resources_pdf = "resources/weekly_main_resources.pdf"
        resources_doc = fitz.open(resources_pdf)
        topic_list = AreaOverlayObject(page_num, Coord(0,0,0), Ratio.mm_to_px(41.8))
        for i in range(len(self.topics)):
            topic_box = AreaOverlayObject(0, Coord(0,0,0), Ratio.mm_to_px(41.8))
            if topic_num == i:
                background = Component(resources_pdf, 8, resources_doc.load_page(8).rect)
            else:
                background = Component(resources_pdf, 7, resources_doc.load_page(7).rect)
            topic_box.add_child(ComponentOverlayObject(0, Coord(0,0,0), background))
            with open('resources/topicWithEnter.json', encoding='UTF8') as file:
                topic_text = json.load(file)[self.topics[i]]
            if topic_num == i:
                topic_text_object = TextOverlayObject(0, Coord(Ratio.mm_to_px(3), Ratio.mm_to_px(6), 0), "resources/fonts/Pretendard-Medium.ttf", 10, topic_text, (1,1,1), fitz.TEXT_ALIGN_LEFT)
            else:
                topic_text_object = TextOverlayObject(0, Coord(Ratio.mm_to_px(3), Ratio.mm_to_px(6), 0), "resources/fonts/Pretendard-Medium.ttf", 10, topic_text, (0,0,0), fitz.TEXT_ALIGN_LEFT)
            topic_box.add_child(topic_text_object)
            topic_box.coord.x = Ratio.mm_to_px(i*45.3)
            topic_page_object = TextOverlayObject(0, Coord(Ratio.mm_to_px(35), Ratio.mm_to_px(15.7), 0), "resources/fonts/Pretendard-Medium.ttf", 7.5, f"{fc_pages[i][0]+4}p", (0,0,0), fitz.TEXT_ALIGN_CENTER)
            topic_box.add_child(topic_page_object)
            topic_list.add_child(topic_box)
        topic_list.coord.x -= Ratio.mm_to_px(41.8) * len(self.topics) + Ratio.mm_to_px(3.5) * (len(self.topics)-1)
        return topic_list
    
    def add_page_num(self, overlayer):
        for num in range(4, overlayer.doc.page_count+4):
            if num % 2:
                page_num_object = TextOverlayObject(num-4, Coord(Ratio.mm_to_px(244), Ratio.mm_to_px(358.5), 4), "resources/fonts/Pretendard-Bold.ttf", 14, f"{num}", (0, 0, 0), fitz.TEXT_ALIGN_RIGHT)
            else:
                page_num_object = TextOverlayObject(num-4, Coord(Ratio.mm_to_px(20), Ratio.mm_to_px(358.5), 4), "resources/fonts/Pretendard-Bold.ttf", 14, f"{num}", (0, 0, 0), fitz.TEXT_ALIGN_LEFT)
            page_num_object.overlay(overlayer, page_num_object.coord)

    def build(self):
        total = fitz.open()
        fc_pages = []
        for topic_set in self.items.items():
            result = fitz.open()
            fb = FlowBuilder(topic_set[0], topic_set[1])
            new_doc = fb.build()
            fc_pages.append((total.page_count, (fb.overlayer.doc.page_count+1)//2))
            result.insert_pdf(new_doc)
            new_doc.save(f"output/result_fb_{topic_set[0]}.pdf")

            overlayer = Overlayer(result)
            overlayer.add_page(Component("resources/weekly_pro_resources.pdf", 4, result.load_page(0).rect))

            mb = MainsolBuilder(topic_set[0], topic_set[1])
            new_doc = mb.build()
            result.insert_pdf(new_doc)
            new_doc.save(f"output/result_mb_{topic_set[0]}.pdf")

            pb = ProblemBuilder(topic_set[0], topic_set[1])
            new_doc = pb.build()
            new_doc.save(f"output/result_pb_{topic_set[0]}.pdf")
            result.insert_pdf(new_doc)
            
            result.save(f"output/result_{topic_set[0]}.pdf")
            total.insert_pdf(result)

        ab = AnswerBuilder(self.items.items())
        new_doc = ab.build()
        total.insert_pdf(new_doc)
        
        sb = SolutionBuilder(self.items.items())
        new_doc = sb.build()
        total.insert_pdf(new_doc)

        overlayer = Overlayer(total)
        for i in range(len(fc_pages)):
            topic_list = self.bake_topic_list(fc_pages[i][0]+1, i, fc_pages)
            topic_list.overlay(overlayer, Coord(Ratio.mm_to_px(250)+topic_list.coord.x, Ratio.mm_to_px(8.5), 0))
            if fc_pages[i][1] == 2:
                topic_list = self.bake_topic_list(fc_pages[i][0]+3, i)
                topic_list.overlay(overlayer, Coord(Ratio.mm_to_px(250)+topic_list.coord.x, Ratio.mm_to_px(8.5), 0))
        self.add_page_num(overlayer)

        total.save("output/build_total.pdf")
        #print(fc_pages)
        pass