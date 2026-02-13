"""URL/webpage processor for extracting web content."""

import logging
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from src.processors.base import BaseProcessor, ProcessedContent

logger = logging.getLogger(__name__)


class URLProcessor(BaseProcessor):
    """Process URLs to extract webpage content.

    Uses trafilatura for article extraction with BeautifulSoup
    as a fallback for general web pages.
    """

    # Pseudo MIME type for URL content
    SUPPORTED_MIMES = ["text/x-url", "text/url"]

    USER_AGENT = (
        "Mozilla/5.0 (compatible; SecureBrainBox/1.0; +https://github.com/ericrisco/securebrainbox)"
    )

    @property
    def supported_mimes(self) -> list[str]:
        return self.SUPPORTED_MIMES

    @property
    def name(self) -> str:
        return "URL Processor"

    def supports(self, mime_type: str) -> bool:
        return mime_type in self.SUPPORTED_MIMES

    async def process(
        self, content: bytes, filename: str | None = None, **kwargs
    ) -> ProcessedContent:
        """Extract content from URL.

        Args:
            content: URL as bytes (will be decoded).
            filename: Ignored for URLs.

        Returns:
            ProcessedContent with extracted webpage text.
        """
        # Decode URL from bytes
        url = content.decode("utf-8").strip() if isinstance(content, bytes) else str(content)

        metadata = {
            "url": url,
            "domain": urlparse(url).netloc,
            "title": None,
            "extractor": None,
        }

        try:
            # Fetch the page
            html = await self._fetch_page(url)

            if not html:
                return ProcessedContent(
                    text="",
                    source=url,
                    source_type="url",
                    metadata=metadata,
                    error="Could not fetch URL",
                )

            # Extract title first
            metadata["title"] = self._extract_title(html)

            # Try trafilatura first (better for articles)
            text = await self._extract_with_trafilatura(html)
            metadata["extractor"] = "trafilatura"

            # Fallback to BeautifulSoup if trafilatura didn't get much
            if not text or len(text) < 100:
                text = self._extract_with_beautifulsoup(html)
                metadata["extractor"] = "beautifulsoup"

            if not text.strip():
                return ProcessedContent(
                    text="",
                    source=metadata.get("title") or url,
                    source_type="url",
                    metadata=metadata,
                    error="Could not extract content from URL",
                )

            # Add title to content
            if metadata.get("title"):
                text = f"# {metadata['title']}\n\n{text}"

            return ProcessedContent(
                text=text, source=metadata.get("title") or url, source_type="url", metadata=metadata
            )

        except Exception as e:
            logger.error(f"URL processing error for {url}: {e}")
            return ProcessedContent(
                text="", source=url, source_type="url", metadata=metadata, error=str(e)
            )

    async def _fetch_page(self, url: str) -> str | None:
        """Fetch webpage HTML."""
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(url, headers={"User-Agent": self.USER_AGENT})
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _extract_title(self, html: str) -> str | None:
        """Extract page title."""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Try og:title first
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                return og_title["content"].strip()

            # Fall back to title tag
            title_tag = soup.find("title")
            if title_tag and title_tag.string:
                return title_tag.string.strip()

            return None
        except Exception:
            return None

    async def _extract_with_trafilatura(self, html: str) -> str:
        """Extract main content using trafilatura."""
        try:
            import trafilatura

            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
            )

            return text or ""
        except ImportError:
            logger.warning("trafilatura not available")
            return ""
        except Exception as e:
            logger.warning(f"trafilatura extraction failed: {e}")
            return ""

    def _extract_with_beautifulsoup(self, html: str) -> str:
        """Fallback extraction using BeautifulSoup."""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Remove unwanted elements
            for element in soup(
                [
                    "script",
                    "style",
                    "nav",
                    "footer",
                    "header",
                    "aside",
                    "form",
                    "noscript",
                    "iframe",
                ]
            ):
                element.decompose()

            # Try to find main content
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find(class_=["content", "post", "entry", "article"])
                or soup.find("body")
            )

            if not main_content:
                return ""

            # Get text
            text = main_content.get_text(separator="\n")

            # Clean up whitespace
            lines = []
            for line in text.splitlines():
                line = line.strip()
                if line:
                    lines.append(line)

            return "\n".join(lines)

        except Exception as e:
            logger.warning(f"BeautifulSoup extraction failed: {e}")
            return ""

    async def process_url(self, url: str) -> ProcessedContent:
        """Convenience method to process a URL string directly."""
        return await self.process(url.encode("utf-8"))


# Global instance
url_processor = URLProcessor()
