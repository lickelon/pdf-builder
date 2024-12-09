from fitz import Rect, Document

class ProblemInfo:
    def __init__(self, page_num: int, rect: Rect) -> None:
        self.page_num = page_num
        self.rect = rect