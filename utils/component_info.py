from fitz import Rect, Document

class ComponentInfo:
    def __init__(self, file: Document, page_num: int, rect: Rect) -> None:
        self.file = file
        self.page_num = page_num
        self.rect = rect