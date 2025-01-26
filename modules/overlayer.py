import fitz
from utils.ratio import Ratio
from utils.coord import Coord
from utils.path import *

class PdfManager:
    def __init__(self):
        self.open_pdfs = {}
    
    def get_doc(self, pdf_file):
        if pdf_file not in self.open_pdfs:
            self.open_pdfs[pdf_file] = fitz.open(pdf_file)
        return self.open_pdfs[pdf_file]

class Overlayer:
    def __init__(self, doc):
        self.doc = doc
        self.pdf_manager = PdfManager()
        pass
    def add_page(self, base):
        rect = base.src_rect
        with fitz.open(base.src_pdf) as file:
            new_page = self.doc.new_page(width=rect.width, height=rect.height)
            new_page.show_pdf_page(fitz.Rect(0,0,rect.width,rect.height), file, base.src_page_num, clip=rect)

    def text_overlay(self, page_num, coord, font_file, size, text, color, text_align):
        font = fitz.Font(fontfile=RESOURCES_PATH+"/fonts/"+font_file)
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
        file = self.pdf_manager.get_doc(component.src_pdf)
        page = self.doc.load_page(page_num)
        page.show_pdf_page(fitz.Rect(coord.x,coord.y,coord.x+component.src_rect.width,coord.y+component.src_rect.height), file, component.src_page_num, clip=component.src_rect)
        pass

    def pdf_overlay_with_resize(self, page_num, coord, component, ratio):
        file = self.pdf_manager.get_doc(component.src_pdf)
        page = self.doc.load_page(page_num)
        page.show_pdf_page(fitz.Rect(coord.x,coord.y,coord.x+component.src_rect.width*ratio,coord.y+component.src_rect.height*ratio), file, component.src_page_num, clip=component.src_rect)
        pass


#TODO: object resolver