import fitz
from docling.document_converter import DocumentConverter
import logging

logger = logging.getLogger(__name__)

class PDFParser:
    """Hybrid PDF parser combining canonical text extraction and structured tables."""

    def __init__(self):
        self.converter = DocumentConverter()

    def extract_tables(self, pdf_path: str):
        """Extract tables from PDF using Docling (faster than full markdown)."""
        doc = self.converter.convert(pdf_path).document
        tables = []

        for table in getattr(doc, "tables", []):
            try:
                tables.append(table.export_to_markdown(doc))
            except Exception as e:
                logger.warning(f"Failed to export table: {e}")

        return tables

    def extract_lines_with_links(self, pdf_path: str):
        """Extract canonical lines with hyperlinks using PyMuPDF."""
        doc = fitz.open(pdf_path)
        lines = []

        for page in doc:
            page_links = page.get_links()
            link_rects = [(fitz.Rect(l["from"]), l["uri"]) for l in page_links if l.get("uri")]

            blocks = sorted(page.get_text("dict")["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))

            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    parts = [span["text"].strip() for span in line["spans"] if span["text"].strip()]
                    if not parts:
                        continue

                    line_text = " ".join(parts)
                    line_rect = fitz.Rect(line["bbox"])

                    for link_rect, uri in link_rects:
                        if line_rect.intersects(link_rect):
                            line_text = f"{line_text} -> {uri}"

                    lines.append(line_text)

        doc.close()
        return lines

    def hybrid_resume_parser(self, pdf_path: str):
        """Combine canonical text lines and structured tables into final text."""
        canonical_lines = self.extract_lines_with_links(pdf_path)
        tables = self.extract_tables(pdf_path)

        final_text = "\n".join(canonical_lines)

        if tables:
            final_text += "\n\n--- TABLES (Structured from Docling) ---\n\n"
            final_text += "\n\n".join(tables)

        return final_text