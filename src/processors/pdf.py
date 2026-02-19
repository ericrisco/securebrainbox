"""PDF document processor."""

import io
import logging

from src.processors.base import BaseProcessor, ProcessedContent

logger = logging.getLogger(__name__)


class PDFProcessor(BaseProcessor):
    """Process PDF documents to extract text.

    Uses pypdf as primary extractor with pdfplumber as fallback
    for better text extraction from complex PDFs.
    """

    SUPPORTED_MIMES = [
        "application/pdf",
    ]

    @property
    def supported_mimes(self) -> list[str]:
        return self.SUPPORTED_MIMES

    @property
    def name(self) -> str:
        return "PDF Processor"

    def supports(self, mime_type: str) -> bool:
        return mime_type in self.SUPPORTED_MIMES

    async def process(
        self, content: bytes, filename: str | None = None, **kwargs
    ) -> ProcessedContent:
        """Extract text from PDF document.

        Args:
            content: PDF file bytes.
            filename: Original filename.

        Returns:
            ProcessedContent with extracted text.
        """
        metadata = {
            "filename": filename,
            "pages": 0,
            "extractor": None,
        }

        try:
            # Try pypdf first (faster, handles most PDFs)
            text = await self._extract_with_pypdf(content, metadata)

            # If pypdf got very little text, try pdfplumber
            if len(text.strip()) < 100:
                logger.info(f"pypdf extracted little text from {filename}, trying pdfplumber")
                text = await self._extract_with_pdfplumber(content, metadata)

            if not text.strip():
                return ProcessedContent(
                    text="",
                    source=filename or "document.pdf",
                    source_type="pdf",
                    metadata=metadata,
                    error="Could not extract text from PDF (may be image-based)",
                )

            return ProcessedContent(
                text=text, source=filename or "document.pdf", source_type="pdf", metadata=metadata
            )

        except Exception as e:
            logger.error(f"PDF processing error for {filename}: {e}")
            return ProcessedContent(
                text="",
                source=filename or "document.pdf",
                source_type="pdf",
                metadata=metadata,
                error=str(e),
            )

    async def _extract_with_pypdf(self, content: bytes, metadata: dict) -> str:
        """Extract text using pypdf."""
        from pypdf import PdfReader

        text_parts = []
        pdf_file = io.BytesIO(content)

        reader = PdfReader(pdf_file)
        metadata["pages"] = len(reader.pages)
        metadata["extractor"] = "pypdf"

        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(f"[Page {page_num + 1}]\n{page_text}")
            except Exception as e:
                logger.warning(f"Error extracting page {page_num + 1}: {e}")
                continue

        return "\n\n".join(text_parts)

    async def _extract_with_pdfplumber(self, content: bytes, metadata: dict) -> str:
        """Extract text using pdfplumber (better for complex layouts)."""
        import pdfplumber

        text_parts = []
        pdf_file = io.BytesIO(content)

        with pdfplumber.open(pdf_file) as pdf:
            metadata["pages"] = len(pdf.pages)
            metadata["extractor"] = "pdfplumber"

            for page_num, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(f"[Page {page_num + 1}]\n{page_text}")
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num + 1}: {e}")
                    continue

        return "\n\n".join(text_parts)


# Global instance
pdf_processor = PDFProcessor()
