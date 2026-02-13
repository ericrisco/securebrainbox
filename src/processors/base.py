"""Base processor interface for content processing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ProcessedContent:
    """Result of content processing.

    Attributes:
        text: Extracted text content.
        source: Source identifier (filename, URL, etc.).
        source_type: Type of content (pdf, image, audio, url).
        metadata: Additional metadata about the content.
        error: Error message if processing failed.
    """
    text: str
    source: str
    source_type: str
    metadata: dict = field(default_factory=dict)
    error: str | None = None

    @property
    def success(self) -> bool:
        """Check if processing was successful."""
        return self.error is None and len(self.text) > 0

    @property
    def char_count(self) -> int:
        """Get character count of extracted text."""
        return len(self.text)


class BaseProcessor(ABC):
    """Base class for content processors.

    All content processors (PDF, image, audio, URL) should inherit
    from this class and implement the abstract methods.
    """

    @abstractmethod
    async def process(
        self,
        content: bytes,
        filename: str | None = None,
        **kwargs
    ) -> ProcessedContent:
        """Process content and extract text.

        Args:
            content: Raw bytes of the content.
            filename: Optional filename for context.
            **kwargs: Additional processor-specific arguments.

        Returns:
            ProcessedContent with extracted text and metadata.
        """
        pass

    @abstractmethod
    def supports(self, mime_type: str) -> bool:
        """Check if this processor supports the given MIME type.

        Args:
            mime_type: MIME type string (e.g., 'application/pdf').

        Returns:
            True if this processor can handle the MIME type.
        """
        pass

    @property
    @abstractmethod
    def supported_mimes(self) -> list[str]:
        """List of supported MIME types."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the processor."""
        pass
