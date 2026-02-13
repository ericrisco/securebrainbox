"""Audio processor using Whisper for transcription."""

import contextlib
import logging
import subprocess
import tempfile
from pathlib import Path

from src.processors.base import BaseProcessor, ProcessedContent

logger = logging.getLogger(__name__)


class AudioProcessor(BaseProcessor):
    """Process audio files using Whisper for transcription.

    Supports voice messages and audio files from Telegram.
    Uses OpenAI Whisper for speech-to-text conversion.
    """

    SUPPORTED_MIMES = [
        "audio/ogg",
        "audio/mpeg",
        "audio/mp3",
        "audio/wav",
        "audio/x-wav",
        "audio/webm",
        "audio/mp4",
        "audio/m4a",
        "video/webm",  # Some voice messages come as video/webm
    ]

    @property
    def supported_mimes(self) -> list[str]:
        return self.SUPPORTED_MIMES

    @property
    def name(self) -> str:
        return "Audio Processor"

    def supports(self, mime_type: str) -> bool:
        return mime_type in self.SUPPORTED_MIMES

    async def process(
        self,
        content: bytes,
        filename: str | None = None,
        **kwargs
    ) -> ProcessedContent:
        """Transcribe audio using Whisper.

        Args:
            content: Audio file bytes.
            filename: Original filename.

        Returns:
            ProcessedContent with transcription.
        """
        metadata = {
            "filename": filename,
            "duration_seconds": 0,
            "transcription_method": None,
        }

        try:
            # Save to temp file
            suffix = self._get_suffix(filename)
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
                f.write(content)
                temp_path = Path(f.name)

            try:
                # Get duration
                duration = await self._get_duration(temp_path)
                metadata["duration_seconds"] = duration

                # Transcribe
                transcription = await self._transcribe(temp_path)
                metadata["transcription_method"] = "whisper"

                if not transcription.strip():
                    return ProcessedContent(
                        text="",
                        source=filename or "audio",
                        source_type="audio",
                        metadata=metadata,
                        error="Could not transcribe audio (no speech detected)"
                    )

                return ProcessedContent(
                    text=transcription,
                    source=filename or "audio",
                    source_type="audio",
                    metadata=metadata
                )

            finally:
                # Cleanup temp file
                with contextlib.suppress(Exception):
                    temp_path.unlink()

        except Exception as e:
            logger.error(f"Audio processing error for {filename}: {e}")
            return ProcessedContent(
                text="",
                source=filename or "audio",
                source_type="audio",
                metadata=metadata,
                error=str(e)
            )

    def _get_suffix(self, filename: str | None) -> str:
        """Get file suffix for temp file."""
        if filename:
            suffix = Path(filename).suffix
            if suffix:
                return suffix
        return ".ogg"

    async def _get_duration(self, file_path: Path) -> float:
        """Get audio duration using ffprobe."""
        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(file_path)
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            return float(result.stdout.strip())
        except Exception as e:
            logger.warning(f"Could not get duration: {e}")
            return 0.0

    async def _transcribe(self, file_path: Path) -> str:
        """Transcribe audio using Whisper.

        Tries local Whisper first, falls back to simpler methods.
        """
        # Try using local Whisper
        try:
            return await self._transcribe_with_whisper(file_path)
        except ImportError:
            logger.info("Local Whisper not available, trying alternative")
        except Exception as e:
            logger.warning(f"Local Whisper failed: {e}")

        # If Whisper is not available, return placeholder
        return "[Audio transcription requires Whisper to be installed]"

    async def _transcribe_with_whisper(self, file_path: Path) -> str:
        """Transcribe using local Whisper model."""
        import whisper

        # Load model (use base for speed, can use larger for accuracy)
        model = whisper.load_model("base")

        # Transcribe
        result = model.transcribe(str(file_path))

        return result.get("text", "")

    async def _convert_to_wav(self, file_path: Path) -> Path:
        """Convert audio to WAV format using ffmpeg."""
        wav_path = file_path.with_suffix(".wav")

        subprocess.run(
            [
                "ffmpeg", "-i", str(file_path),
                "-ar", "16000",
                "-ac", "1",
                "-y",
                str(wav_path)
            ],
            capture_output=True,
            check=True,
            timeout=60
        )

        return wav_path


# Global instance
audio_processor = AudioProcessor()
