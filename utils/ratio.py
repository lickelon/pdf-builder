from fitz import Rect

class Ratio:
    PDF_DPI = 72

    @staticmethod
    def mm_to_px(mm: float | int) -> float:
        return mm * Ratio.PDF_DPI / 25.4
    
    @staticmethod
    def rect_mm_to_px(rect):
        _rect = Rect(rect)
        _rect.x0 = Ratio.mm_to_px(rect.x0)
        _rect.x1 = Ratio.mm_to_px(rect.x1)
        _rect.y0 = Ratio.mm_to_px(rect.y0)
        _rect.y1 = Ratio.mm_to_px(rect.y1)
        return _rect
    
    @staticmethod
    def px_to_mm(px: float | int) -> float:
        return px / Ratio.PDF_DPI * 25.4
    
    @staticmethod
    def dpi_to_scale(dpi: int) -> float:
        return dpi / Ratio.PDF_DPI