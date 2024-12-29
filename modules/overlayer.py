import fitz
from utils.ratio import Ratio
from utils.coord import Coord

class Overlayer:
    def __init__(self, doc):
        self.doc = doc
        pass
    def add_page(self, base):
        rect = base.src_rect
        with fitz.open(base.src_pdf) as file:
            new_page = self.doc.new_page(width=rect.width, height=rect.height)
            new_page.show_pdf_page(fitz.Rect(0,0,rect.width,rect.height), file, base.src_page_num, clip=rect)

    def text_overlay(self, page_num, coord, font_file, size, text, color, text_align):
        font = fitz.Font(fontfile=font_file)
        page = self.doc.load_page(page_num)
        tw = fitz.TextWriter(page.rect)
        x = coord.x
        y = coord.y
        if text_align == fitz.TEXT_ALIGN_CENTER:
            x -= font.text_length(text, size) / 2
        elif text_align == fitz.TEXT_ALIGN_RIGHT:
            x -= font.text_length(text, size)
        
        tw.append((x, y), text, font, size)
        tw.write_text(page, color=color)
        pass

    def shape_overlay(self, page_num, coord, rect, color, radius = None):
        page = self.doc.load_page(page_num)
        page.draw_rect(fitz.Rect(coord.x, coord.y, coord.x + rect.width, coord.y + rect.height), color=color, fill=color, radius=radius)

    def pdf_overlay(self, page_num, coord, component):
        with fitz.open(component.src_pdf) as file:
            page = self.doc.load_page(page_num)
            page.show_pdf_page(fitz.Rect(coord.x,coord.y,coord.x+component.src_rect.width,coord.y+component.src_rect.height), file, component.src_page_num, clip=component.src_rect)
        pass


#TODO: object resolver