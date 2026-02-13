"""Tests for content processors."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.processors.base import ProcessedContent


class TestProcessedContent:
    """Test ProcessedContent dataclass."""
    
    def test_success_with_text(self):
        """Test success property with text."""
        content = ProcessedContent(
            text="Some content",
            source="test.pdf",
            source_type="pdf"
        )
        assert content.success is True
    
    def test_success_without_text(self):
        """Test success property without text."""
        content = ProcessedContent(
            text="",
            source="test.pdf",
            source_type="pdf"
        )
        assert content.success is False
    
    def test_success_with_error(self):
        """Test success property with error."""
        content = ProcessedContent(
            text="Some content",
            source="test.pdf",
            source_type="pdf",
            error="Something went wrong"
        )
        assert content.success is False
    
    def test_char_count(self):
        """Test char_count property."""
        content = ProcessedContent(
            text="Hello world",
            source="test",
            source_type="text"
        )
        assert content.char_count == 11


class TestPDFProcessor:
    """Test PDF processor."""
    
    def test_supports_pdf_mime(self):
        """Test that PDF processor supports PDF MIME type."""
        from src.processors.pdf import pdf_processor
        
        assert pdf_processor.supports("application/pdf")
        assert not pdf_processor.supports("image/png")
    
    def test_processor_name(self):
        """Test processor name."""
        from src.processors.pdf import pdf_processor
        
        assert pdf_processor.name == "PDF Processor"
    
    @pytest.mark.asyncio
    async def test_process_empty_bytes(self):
        """Test processing empty bytes returns error."""
        from src.processors.pdf import pdf_processor
        
        result = await pdf_processor.process(b"", "test.pdf")
        
        assert result.source == "test.pdf"
        assert result.source_type == "pdf"
        assert result.error is not None


class TestImageProcessor:
    """Test image processor."""
    
    def test_supports_image_mimes(self):
        """Test that image processor supports image MIME types."""
        from src.processors.image import image_processor
        
        assert image_processor.supports("image/jpeg")
        assert image_processor.supports("image/png")
        assert image_processor.supports("image/gif")
        assert not image_processor.supports("application/pdf")
    
    def test_processor_name(self):
        """Test processor name."""
        from src.processors.image import image_processor
        
        assert image_processor.name == "Image Processor"


class TestAudioProcessor:
    """Test audio processor."""
    
    def test_supports_audio_mimes(self):
        """Test that audio processor supports audio MIME types."""
        from src.processors.audio import audio_processor
        
        assert audio_processor.supports("audio/ogg")
        assert audio_processor.supports("audio/mpeg")
        assert audio_processor.supports("audio/wav")
        assert not audio_processor.supports("application/pdf")
    
    def test_processor_name(self):
        """Test processor name."""
        from src.processors.audio import audio_processor
        
        assert audio_processor.name == "Audio Processor"


class TestURLProcessor:
    """Test URL processor."""
    
    def test_supports_url_mimes(self):
        """Test that URL processor supports URL pseudo MIME types."""
        from src.processors.url import url_processor
        
        assert url_processor.supports("text/x-url")
        assert url_processor.supports("text/url")
        assert not url_processor.supports("application/pdf")
    
    def test_processor_name(self):
        """Test processor name."""
        from src.processors.url import url_processor
        
        assert url_processor.name == "URL Processor"
    
    @pytest.mark.asyncio
    async def test_extract_title(self):
        """Test title extraction from HTML."""
        from src.processors.url import url_processor
        
        html = "<html><head><title>Test Page</title></head><body></body></html>"
        title = url_processor._extract_title(html)
        
        assert title == "Test Page"
    
    @pytest.mark.asyncio
    async def test_extract_title_og(self):
        """Test title extraction from og:title."""
        from src.processors.url import url_processor
        
        html = '''
        <html>
        <head>
            <meta property="og:title" content="OG Title">
            <title>Regular Title</title>
        </head>
        <body></body>
        </html>
        '''
        title = url_processor._extract_title(html)
        
        assert title == "OG Title"


class TestProcessorManager:
    """Test processor manager."""
    
    def test_get_processor_pdf(self):
        """Test getting PDF processor."""
        from src.processors import processor_manager
        
        processor = processor_manager.get_processor("application/pdf")
        
        assert processor is not None
        assert processor.name == "PDF Processor"
    
    def test_get_processor_image(self):
        """Test getting image processor."""
        from src.processors import processor_manager
        
        processor = processor_manager.get_processor("image/jpeg")
        
        assert processor is not None
        assert processor.name == "Image Processor"
    
    def test_get_processor_unsupported(self):
        """Test getting processor for unsupported type."""
        from src.processors import processor_manager
        
        processor = processor_manager.get_processor("application/unknown")
        
        assert processor is None
    
    def test_is_supported(self):
        """Test is_supported method."""
        from src.processors import processor_manager
        
        assert processor_manager.is_supported("application/pdf")
        assert processor_manager.is_supported("image/png")
        assert not processor_manager.is_supported("application/unknown")
    
    def test_get_supported_types(self):
        """Test getting all supported types."""
        from src.processors import processor_manager
        
        types = processor_manager.get_supported_types()
        
        assert "PDF Processor" in types
        assert "Image Processor" in types
        assert "Audio Processor" in types
        assert "URL Processor" in types
    
    def test_get_all_supported_mimes(self):
        """Test getting flat list of supported MIME types."""
        from src.processors import processor_manager
        
        mimes = processor_manager.get_all_supported_mimes()
        
        assert "application/pdf" in mimes
        assert "image/jpeg" in mimes
        assert "audio/ogg" in mimes
    
    @pytest.mark.asyncio
    async def test_process_unsupported_type(self):
        """Test processing unsupported content type."""
        from src.processors import processor_manager
        
        result = await processor_manager.process(
            content=b"test",
            mime_type="application/unknown",
            filename="test.xyz"
        )
        
        assert result.error is not None
        assert "Unsupported" in result.error
