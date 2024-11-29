class Ratio:
    PDF_DPI = 72

    @staticmethod
    def mm_to_px(mm: float | int) -> float:
        return mm * Ratio.PDF_DPI / 25.4
    
    @staticmethod
    def px_to_mm(px: float | int) -> float:
        return px / Ratio.PDF_DPI * 25.4
    
    @staticmethod
    def dpi_to_scale(dpi: int) -> float:
        return dpi / Ratio.PDF_DPI