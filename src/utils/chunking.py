"""Text chunking utilities for document processing."""

import logging
from dataclasses import dataclass

from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""

    content: str
    index: int
    start_char: int
    end_char: int

    @property
    def length(self) -> int:
        """Length of the chunk content."""
        return len(self.content)


class TextChunker:
    """Chunk text into smaller pieces for embedding.

    Uses RecursiveCharacterTextSplitter from LangChain for intelligent
    text splitting that preserves semantic boundaries.

    Attributes:
        chunk_size: Target size for each chunk.
        chunk_overlap: Number of characters to overlap between chunks.
    """

    DEFAULT_SEPARATORS = [
        "\n\n",  # Paragraphs
        "\n",  # Lines
        ". ",  # Sentences
        "? ",  # Questions
        "! ",  # Exclamations
        "; ",  # Semicolons
        ", ",  # Commas
        " ",  # Words
        "",  # Characters (fallback)
    ]

    def __init__(
        self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: list[str] | None = None
    ):
        """Initialize the text chunker.

        Args:
            chunk_size: Maximum size of each chunk. Default 1000.
            chunk_overlap: Characters to overlap between chunks. Default 200.
            separators: List of separators to try, in order. Uses defaults if None.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.separators,
            length_function=len,
            is_separator_regex=False,
        )

        logger.info(f"TextChunker initialized: size={chunk_size}, overlap={chunk_overlap}")

    def chunk(self, text: str) -> list[str]:
        """Split text into chunks.

        Args:
            text: The text to split.

        Returns:
            List of text chunks.
        """
        if not text or not text.strip():
            return []

        chunks = self._splitter.split_text(text)
        logger.debug(f"Split text into {len(chunks)} chunks")

        return chunks

    def chunk_with_metadata(
        self, text: str, source: str, source_type: str, extra_metadata: dict | None = None
    ) -> list[dict]:
        """Split text and attach metadata to each chunk.

        Args:
            text: The text to split.
            source: Source identifier (filename, URL, etc.).
            source_type: Type of source (text, pdf, url, etc.).
            extra_metadata: Additional metadata to attach.

        Returns:
            List of dicts with content and metadata for each chunk.
        """
        if not text or not text.strip():
            return []

        chunks = self.chunk(text)

        result = []
        for i, chunk_content in enumerate(chunks):
            chunk_data = {
                "content": chunk_content,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "source": source,
                "source_type": source_type,
            }

            if extra_metadata:
                chunk_data["metadata"] = extra_metadata

            result.append(chunk_data)

        logger.info(f"Created {len(result)} chunks from {source} ({source_type})")

        return result

    def estimate_chunks(self, text: str) -> int:
        """Estimate the number of chunks without actually splitting.

        Args:
            text: The text to estimate.

        Returns:
            Estimated number of chunks.
        """
        if not text:
            return 0

        text_length = len(text)
        effective_chunk_size = self.chunk_size - self.chunk_overlap

        if text_length <= self.chunk_size:
            return 1

        return max(1, (text_length - self.chunk_overlap) // effective_chunk_size + 1)


# Global chunker instance with default settings
text_chunker = TextChunker()

# Chunker for smaller chunks (useful for precise search)
precise_chunker = TextChunker(chunk_size=500, chunk_overlap=100)

# Chunker for larger chunks (useful for context)
context_chunker = TextChunker(chunk_size=2000, chunk_overlap=400)
