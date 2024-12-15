from fitz import Rect
from utils.component import Component, ComponentType
from utils.coord import Coord
import copy

class OverlayObject():
    def __init__(self, page_num: int, coord: Coord):
        self.page_num = page_num
        self.coord = coord
        self.child = []
    
    def add_child(self, obj: 'OverlayObject'):
        self.child.append(copy.deepcopy(obj))

    def overlay(self, overlayer, page_num, absolute_coord):
        for oo in self.child:
            oo.overlay(overlayer, page_num, absolute_coord + oo.coord)
        pass

    def get_height(self):
        pass

class ListOverlayObject(OverlayObject):
    def __init__(self, page_num, coord, height, align):
        super().__init__(page_num, coord)
        self.ls = []
        self.height = height
        self.align = align
        self.left_height = height

    def overlay(self, overlayer, page_num, absolute_coord):
        #TODO
        if self.align == 0:
            curr_height = 0
            for oo in self.child:
                oo.overlay(overlayer, page_num, absolute_coord + Coord(0, curr_height, 0))
                curr_height += oo.get_height()
        pass
    def add_child(self, obj: OverlayObject):
        if obj.get_height() > self.left_height:
            return False
        else:
            new_obj = copy.deepcopy(obj)
            #new_obj.page_num = self.page_num
            self.child.append(new_obj)
            self.left_height -= obj.get_height()
        return True
    pass

class ParagraphOverlayObject(OverlayObject):
    def __init__(self):
        self.child = []
    
    def add_paragraph_list(self, paragraph_list: ListOverlayObject):
        self.child.append(copy.deepcopy(paragraph_list))

    def add_child(self, obj: 'OverlayObject'):
        if self.child and self.child[-1].add_child(obj):
            return True
            pass
        else:
            #should append new list
            return False
        
    def overlay(self, overlayer, page_num, absolute_coord):
        for oo in self.child:
            oo.overlay(overlayer, oo.page_num, absolute_coord + oo.coord)
        pass


class AreaOverlayObject(OverlayObject):
    def __init__(self, page_num, coord, height):
        self.height = height
        super().__init__(page_num, coord)

    def get_height(self):
        return self.height

class ComponentOverlayObject(OverlayObject):
    def __init__(self, page_num, coord, component):
        self.component = component
        super().__init__(page_num, coord)

    def overlay(self, overlayer, page_num, absolute_coord):
        overlayer.pdf_overlay(page_num, absolute_coord, self.component)
        super().overlay(overlayer, page_num, absolute_coord)
    pass

    def get_height(self):
        return self.component.src_rect.height

class TextOverlayObject(OverlayObject):
    def __init__(self, page_num, coord, font, size, text, color, text_align):
        self.font = font
        self.size = size
        self.text = text
        self.color = color
        self.text_align = text_align
        super().__init__(page_num, coord)

    def overlay(self, overlayer, page_num, absolute_coord):
        overlayer.text_overlay(page_num, absolute_coord, self.font, self.size, self.text, self.color, self.text_align)
        super().overlay(overlayer, page_num, absolute_coord)

    def get_height(self):
        #Error: text in paragraph should be wrapped by area
        return None

