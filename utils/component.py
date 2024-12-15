from fitz import Rect
from enum import Enum

class ComponentType(Enum):
    a = 0
    pass
class Component:
    def __init__(self, src_pdf: str, src_page_num: int, src_rect: Rect, component_type: ComponentType = None):
        self.src_pdf = src_pdf
        self.src_page_num = src_page_num
        self.src_rect = src_rect
        if component_type is not None: self.component_type = component_type

    