import fitz
from fitz import Page, Rect
import numpy as np
import os

from utils.direction import Direction
from utils.pdf_utils import PdfUtils
from utils.ratio import Ratio
from utils.problem_info import ProblemInfo

class KiceCropper:
    def __init__(self, pdf_name: str) -> None:
        self.pdf_name = pdf_name
        self.base_name = os.path.basename(self.pdf_name)

    def get_problems_area(self, page: Page, accuracy = 1, offset = 1) -> Rect:
        #trim left and right
        rect = page.rect
        new_rect = PdfUtils.trim_whitespace(page, rect, Direction.LEFT, accuracy)
        new_rect.x1 -= new_rect.x0 - rect.x0

        #trim up and down
        na = PdfUtils.pdf_clip_to_array(page, new_rect, fitz.Matrix(1, accuracy))
        na = na.mean(axis=1, dtype=np.uint32)
        na = np.where(na < 10, 0, na)
        na = na.mean(axis=1, dtype=np.uint32)
        
        upper_bound = na.argmin()
        lower_bound = 0
        flag = False
        for y in range(upper_bound, na.shape[0]):
            if na[y] == 255:
                lower_bound = y
                break

        new_rect.y0 = upper_bound / accuracy
        new_rect.y1 = lower_bound / accuracy
        new_rect.y0 += offset
        new_rect.y1 += offset

        return new_rect

    def get_problem_rects(self, page: Page, accuracy = 1) -> list[Rect]:
        rects = []
        area = self.get_problems_area(page, accuracy, offset=2)

        mid = (area.x0 + area.x1) / 2

        left_area = Rect(area)
        left_area.x1 = mid - Ratio.mm_to_px(5)
        left_area = PdfUtils.trim_whitespace(page, left_area, Direction.RIGHT, accuracy)
        left_area.x0 = left_area.x1 - Ratio.mm_to_px(112.5)
        #left_area.x1 += Ratio.mm_to_px(0.5)
        rects += self.get_problem_rects_from_area(page, left_area, accuracy)

        right_area = Rect(area)
        right_area = PdfUtils.trim_whitespace(page, right_area, Direction.RIGHT, accuracy)
        right_area.x0 = right_area.x1 - Ratio.mm_to_px(112.5)
        #right_area.x1 += Ratio.mm_to_px(0.5)
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
    
    def get_problem_infos_from_file(self, file: fitz.Document, accuracy = 1) -> list[ProblemInfo]:
        ret = []
        for page_num in range(file.page_count):
            page = file.load_page(page_num)
            rects = self.get_problem_rects(page, accuracy)
            for rect in rects:
                ret.append(ProblemInfo(page_num, rect))
        ret.pop()
        return ret

    def extract_problems(self, accuracy = 1) -> int:
        with fitz.open(self.pdf_name) as file:
            self.infos = self.get_problem_infos_from_file(file, accuracy)
            return len(self.infos)

    def save_original(self) -> None:
        with fitz.open(self.pdf_name) as file:
            for i in range(len(self.infos)):
                PdfUtils.extract_to_pdf(file, self.infos[i].page_num, self.infos[i].rect, f"output/original/{self.base_name[:-7]} {i+1}번 {self.base_name[-6:-4]}_original.pdf")

    def save_caption(self, caption_point: tuple, font_size: int) -> None:
        with fitz.open(self.pdf_name) as file:
            for i in range(len(self.infos)):
                rect = self.infos[i].rect
                new_doc = fitz.open()
                new_page = new_doc.new_page(width=rect.width, height=rect.height+Ratio.mm_to_px(caption_point[1]))
                new_page.show_pdf_page(fitz.Rect(0, Ratio.mm_to_px(caption_point[1]),rect.width,rect.height+Ratio.mm_to_px(caption_point[1])), file, self.infos[i].page_num, clip=rect)
                new_page.draw_rect(fitz.Rect(0, Ratio.mm_to_px(caption_point[1]), Ratio.mm_to_px(6), Ratio.mm_to_px(caption_point[1]+5)), color=(1,1,1), fill=(1,1,1))
                font = fitz.Font(fontfile="Eulyoo1945-Regular.ttf")
                tw = fitz.TextWriter(new_page.rect)
                tw.append((Ratio.mm_to_px(caption_point[0]), font_size), f"{os.path.basename(self.pdf_name)[:-4]} {i+1}번 지1", font, font_size)
                tw.write_text(new_page, color=(0,0,0))
                new_doc.save(f"output/caption/{self.base_name[:-7]} {i+1}번 {self.base_name[-6:-4]}_caption.pdf")
                #PdfUtils.extract_to_pdf(file, infos[i].page_num, infos[i].rect, f"output/caption/{os.path.basename(pdf_name)[:-4]} {i+1}번 지1_caption.pdf")