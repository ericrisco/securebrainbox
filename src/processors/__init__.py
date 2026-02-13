"""Content processors for various file formats.

This module provides processors for extracting text from different
content types: PDFs, images, audio, and URLs.
"""

import logging

from src.processors.audio import audio_processor
from src.processors.base import BaseProcessor, ProcessedContent
from src.processors.image import image_processor
from src.processors.pdf import pdf_processor
from src.processors.url import url_processor

logger = logging.getLogger(__name__)

# Export classes and instances
__all__ = [
    "BaseProcessor",
    "ProcessedContent",
    "ProcessorManager",
    "processor_manager",
    "pdf_processor",
    "image_processor",
    "audio_processor",
    "url_processor",
]


class ProcessorManager:
    """Manages all content processors.

    Provides a unified interface for processing different content types
    by automatically selecting the appropriate processor based on MIME type.
    """

    def __init__(self):
        """Initialize with all available processors."""
        self.processors: list[BaseProcessor] = [
            pdf_processor,
            image_processor,
            audio_processor,
            url_processor,
        ]

        logger.info(f"ProcessorManager initialized with {len(self.processors)} processors")

    def get_processor(self, mime_type: str) -> BaseProcessor | None:
        """Get the appropriate processor for a MIME type.

        Args:
            mime_type: MIME type string.

        Returns:
            Matching processor or None if not supported.
        """
        for processor in self.processors:
            if processor.supports(mime_type):
                return processor
        return None

    def is_supported(self, mime_type: str) -> bool:
        """Check if a MIME type is supported.

        Args:
            mime_type: MIME type string.

        Returns:
            True if any processor supports this MIME type.
        """
        return self.get_processor(mime_type) is not None

    async def process(
        self, content: bytes, mime_type: str, filename: str | None = None, **kwargs
    ) -> ProcessedContent:
        """Process content with the appropriate processor.

        Args:
            content: Raw bytes of the content.
            mime_type: MIME type of the content.
            filename: Optional filename.
            **kwargs: Additional processor-specific arguments.

        Returns:
            ProcessedContent with extracted text and metadata.
        """
        processor = self.get_processor(mime_type)

        if not processor:
            logger.warning(f"No processor for MIME type: {mime_type}")
            return ProcessedContent(
                text="",
                source=filename or "unknown",
                source_type="unknown",
                metadata={"mime_type": mime_type},
                error=f"Unsupported content type: {mime_type}",
            )

        logger.info(f"Processing {filename or 'content'} with {processor.name}")
        return await processor.process(content, filename, **kwargs)

    def get_supported_types(self) -> dict[str, list[str]]:
        """Get all supported MIME types grouped by processor.

        Returns:
            Dict mapping processor names to their supported MIME types.
        """
        return {processor.name: processor.supported_mimes for processor in self.processors}

    def get_all_supported_mimes(self) -> list[str]:
        """Get flat list of all supported MIME types.

        Returns:
            List of all supported MIME type strings.
        """
        mimes = []
        for processor in self.processors:
            mimes.extend(processor.supported_mimes)
        return mimes


# Global processor manager instance
processor_manager = ProcessorManager()
