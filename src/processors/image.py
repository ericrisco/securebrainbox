"""Image processor using vision model for description."""

import base64
import io
import logging

from PIL import Image

from src.config import settings
from src.processors.base import BaseProcessor, ProcessedContent

logger = logging.getLogger(__name__)


class ImageProcessor(BaseProcessor):
    """Process images using vision model for description.

    Uses Ollama's vision capabilities (if available) to generate
    text descriptions of images for indexing.
    """

    SUPPORTED_MIMES = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/bmp",
    ]

    @property
    def supported_mimes(self) -> list[str]:
        return self.SUPPORTED_MIMES

    @property
    def name(self) -> str:
        return "Image Processor"

    def supports(self, mime_type: str) -> bool:
        return mime_type in self.SUPPORTED_MIMES

    async def process(
        self,
        content: bytes,
        filename: str | None = None,
        caption: str | None = None,
        **kwargs
    ) -> ProcessedContent:
        """Extract description from image using vision model.

        Args:
            content: Image file bytes.
            filename: Original filename.
            caption: User-provided caption for the image.

        Returns:
            ProcessedContent with image description.
        """
        metadata = {
            "filename": filename,
            "width": 0,
            "height": 0,
            "format": None,
            "has_caption": caption is not None,
        }

        try:
            # Get image info
            img = Image.open(io.BytesIO(content))
            metadata["width"] = img.width
            metadata["height"] = img.height
            metadata["format"] = img.format
            metadata["mode"] = img.mode

            # Convert to base64 for vision model
            b64_image = base64.b64encode(content).decode("utf-8")

            # Try to get description from vision model
            description = await self._describe_image(b64_image, caption)

            # Combine caption and description if both available
            text_parts = []
            if caption:
                text_parts.append(f"Caption: {caption}")
            if description:
                text_parts.append(f"Description: {description}")

            text = "\n\n".join(text_parts) if text_parts else ""

            if not text:
                return ProcessedContent(
                    text="",
                    source=filename or "image",
                    source_type="image",
                    metadata=metadata,
                    error="Could not generate image description"
                )

            return ProcessedContent(
                text=text,
                source=filename or "image",
                source_type="image",
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Image processing error for {filename}: {e}")
            return ProcessedContent(
                text=caption or "",  # At least use caption if available
                source=filename or "image",
                source_type="image",
                metadata=metadata,
                error=str(e) if not caption else None
            )

    async def _describe_image(
        self,
        b64_image: str,
        caption: str | None = None
    ) -> str:
        """Get image description using vision model.

        Args:
            b64_image: Base64 encoded image.
            caption: Optional user caption for context.

        Returns:
            Generated description string.
        """
        try:
            import ollama

            client = ollama.Client(host=settings.ollama_host)

            # Build prompt
            prompt = "Describe this image in detail. What do you see? "
            if caption:
                prompt += f"The user provided this caption: '{caption}'. "
            prompt += "Focus on important details, text visible in the image, and key information."

            # Try using vision capabilities
            response = client.chat(
                model=settings.ollama_model,
                messages=[{
                    "role": "user",
                    "content": prompt,
                    "images": [b64_image]
                }]
            )

            return response.get("message", {}).get("content", "")

        except Exception as e:
            logger.warning(f"Vision model failed: {e}")

            # If vision fails but we have a caption, that's still useful
            if caption:
                return ""

            # Return a placeholder
            return "[Image] Description not available - vision model not configured or image not supported"


# Global instance
image_processor = ImageProcessor()
