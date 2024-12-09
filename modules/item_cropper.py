import fitz
from fitz import Page, Rect
import numpy as np
import os

from utils.direction import Direction
from utils.pdf_utils import PdfUtils
from utils.ratio import Ratio
from utils.problem_info import ProblemInfo
from utils.solution_info import SolutionInfo

class ItemCropper:
    def __init__(self):
        pass

    def get_problem_area(self) -> Rect:
        rect = Rect(23, 13, 135.5, 420)
        return Ratio.rect_mm_to_px(rect)
    
    def get_problem_rect(self, page: Page, accuracy = 1) -> Rect:
        area = self.get_problem_area()
        na = PdfUtils.pdf_clip_to_array(page, area, fitz.Matrix(1, accuracy))
        na = na.mean(axis=1, dtype=np.uint32) // 255

        red_line = 0
        for y in range(na.shape[0])[::-1]:
            if np.array_equal(na[y], [1,0,0]):
                red_line = y
                break
        
        area.y1 = area.y0 + y / accuracy - Ratio.mm_to_px(1) - 1

        problem_rect = PdfUtils.trim_whitespace(page, area, Direction.DOWN, accuracy)
        return problem_rect
    
    def rgb_normalize(self, na : np.ndarray) -> np.ndarray:
        na = 255 - (((270 - na) // 30) * 30)
        na = np.where(na > 255, 0, na)
        return na
    
    def rgb_to_hex(self, r, g, b):
        return f"{r:02X}{g:02X}{b:02X}"
    
    def get_solution_component_area(self):
        rect = Rect(174, 0, 274, 420)
        return Ratio.rect_mm_to_px(rect)
    
    def get_solution_bar_area(self):
        rect = Rect(140, 0, 142, 420)
        return Ratio.rect_mm_to_px(rect)

    def get_solution_infos_from_file(self, file: fitz.Document, accuracy = 1) -> list[SolutionInfo]:
        page = file.load_page(0)
        rect = self.get_solution_bar_area()
        na = PdfUtils.pdf_clip_to_array(page, rect, fitz.Matrix(1, accuracy))
        na = self.rgb_normalize(na)

        solutions = dict()
        for y in range(na.shape[0]):
            for x in range(na.shape[1]):
                if np.count_nonzero(na[y][x]) == 1:
                    curr = na[y][x]
                    hexcode = self.rgb_to_hex(curr[0], curr[1], curr[2])
                    if hexcode in solutions:
                        solutions[hexcode].rect.y0 = min(solutions[hexcode].rect.y0, y / accuracy)
                        solutions[hexcode].rect.y1 = max(solutions[hexcode].rect.y1, y / accuracy)
                    else:
                        solutions[hexcode] = SolutionInfo(hexcode, self.get_solution_component_area())
                        solutions[hexcode].rect.y0 = y / accuracy
                        solutions[hexcode].rect.y1 = y / accuracy
        
        #srect = solutions["00FF00"].rect
        #text = page.get_text("text", clip=srect)
        #print(text[2:])

        return list(solutions.values())