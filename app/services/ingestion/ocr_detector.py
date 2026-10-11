from typing import Tuple
import fitz  # PyMuPDF


class OCRDetector:
    """
    Detects whether a PDF document is a scanned image or contains extractable text streams.
    """

    @staticmethod
    def inspect_pdf_scanned_state(pdf_bytes: bytes, threshold_chars_per_page: int = 50) -> Tuple[bool, bool, str]:
        """
        Returns (is_scanned, ocr_required, reason)
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            if len(doc) == 0:
                return True, True, "PDF has 0 pages"

            total_chars = 0
            image_pages = 0

            for page_idx in range(len(doc)):
                page = doc[page_idx]
                text = page.get_text().strip()
                total_chars += len(text)
                images = page.get_images()
                if len(images) > 0 and len(text) < threshold_chars_per_page:
                    image_pages += 1

            num_pages = len(doc)
            avg_chars = total_chars / num_pages if num_pages > 0 else 0
            doc.close()

            if total_chars == 0:
                return True, True, "No extractable text found in PDF. Scanned document requires OCR."

            if avg_chars < threshold_chars_per_page and image_pages > 0:
                return True, True, f"Low text density ({avg_chars:.1f} chars/page) with image raster pages. Document requires OCR."

            return False, False, f"Digital PDF with extractable text streams ({avg_chars:.1f} avg chars/page)."
        except Exception as e:
            return False, False, f"Could not determine scanned status: {str(e)}"
