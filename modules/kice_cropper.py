import fitz
from fitz import Page, Rect
import numpy as np
import os

from utils.direction import Direction
from utils.pdf_utils import PdfUtils
from utils.ratio import Ratio
from utils.component_info import ComponentInfo

class KiceCropper:
    def get_problems_area(self, page: Page, accuracy = 1, offset = 1) -> Rect:
        #trim left and right
        rect = page.rect
        new_rect = PdfUtils.trim_whitespace(page, rect, Direction.LEFT, accuracy)
        new_rect.x1 -= new_rect.x0 - rect.x0

        #trim up and down
        na = PdfUtils.pdf_clip_to_array(page, new_rect, fitz.Matrix(1, accuracy))
        na = na.mean(axis=1, dtype=np.uint32)
        na = np.where(na < 10, 0, na)
        
        upper_bound = 0
        lower_bound = 0
        flag = False
        for y in range(na.shape[0]):
            if np.array_equal(na[y], [0,0,0]):
                upper_bound = y
                flag = True
            elif flag and np.array_equal(na[y], [255,255,255]):
                lower_bound = y
                break

        new_rect.y0 = upper_bound / accuracy
        new_rect.y1 = lower_bound / accuracy
        new_rect.y0 += offset
        new_rect.y1 += offset

        return new_rect

    def get_problem_rects(self, page: Page, accuracy = 1) -> list[Rect]:
        rects = []
        area = self.get_problems_area(page, accuracy)

        left_area = Rect(area)
        left_area.x0 = Ratio.mm_to_px(31)
        left_area.x1 = Ratio.mm_to_px(143.5)
        rects += self.get_problem_rects_from_area(page, left_area, accuracy)

        right_area = Rect(area)
        right_area.x0 = Ratio.mm_to_px(154)
        right_area.x1 = Ratio.mm_to_px(266.5)
        rects += self.get_problem_rects_from_area(page, right_area, accuracy)

        return rects

    def get_problem_rects_from_area(self, page: Page, area: Rect, accuracy = 1, number_offset = 8) -> list[Rect]:
        number_rect = PdfUtils.trim_whitespace(page, area, Direction.LEFT, accuracy)
        number_rect.x1 = number_rect.x0 + number_offset

        na = PdfUtils.pdf_clip_to_array(page, number_rect, fitz.Matrix(1, accuracy))
        na = na.mean(axis=1, dtype=np.uint32) // 255
        
        upper_bounds = []
        flag = False
        for y in range(na.shape[0]):
            if np.array_equal(na[y], [1,1,1]):
                flag = True
            elif flag and np.array_equal(na[y], [0,0,0]):
                flag = False
                upper_bounds.append(y)

        lower_bounds = upper_bounds[1:] + [na.shape[0]]
        for i in range(len(lower_bounds)):
            lower_bounds[i] -= accuracy
            
        rects = []
        for i in range(len(upper_bounds)):
            new_rect = Rect(area)
            new_rect.y1 = new_rect.y0 + lower_bounds[i] / accuracy
            new_rect.y0 += upper_bounds[i] / accuracy
            rects.append(new_rect)
        
        ret = []
        for rect in rects:
            new_rect = PdfUtils.trim_whitespace(page, rect, Direction.DOWN, accuracy)
            new_rect.y0 -= Ratio.mm_to_px(0.5)
            ret.append(new_rect)

        return ret
    
    def get_problem_infos_from_file(self, file: fitz.Document, accuracy = 1) -> list[ComponentInfo]:
        ret = []
        for page_num in range(file.page_count):
            page = file.load_page(page_num)
            rects = self.get_problem_rects(page, accuracy)
            for rect in rects:
                ret.append(ComponentInfo(file, page_num, rect))
        ret.pop()
        return ret

    def extract_problems_to_original(self, pdf_name: str, accuracy = 1) -> None:
        with fitz.open(pdf_name) as file:
            infos = self.get_problem_infos_from_file(file, accuracy)
            for i in range(len(infos)):
                PdfUtils.extract_to_pdf(file, infos[i].page_num, infos[i].rect, f"output/original/{os.path.basename(pdf_name)[:-4]} {i+1}번 지1.pdf")