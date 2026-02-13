"""LLM client using Ollama."""

import logging
from collections.abc import AsyncGenerator

import ollama

from src.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for LLM inference via Ollama.

    Provides methods for generating text responses using the configured
    LLM model, with support for system prompts and streaming.

    Attributes:
        client: Ollama client instance.
        model: Name of the LLM model to use.
    """

    def __init__(self, host: str | None = None, model: str | None = None):
        """Initialize the LLM client.

        Args:
            host: Ollama server URL. Defaults to settings.ollama_host.
            model: LLM model name. Defaults to settings.ollama_model.
        """
        self.host = host or settings.ollama_host
        self.model = model or settings.ollama_model
        self._client: ollama.Client | None = None
        logger.info(f"LLMClient initialized with model: {self.model}")

    @property
    def client(self) -> ollama.Client:
        """Lazy initialization of Ollama client."""
        if self._client is None:
            self._client = ollama.Client(host=self.host)
        return self._client

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The user's prompt/question.
            system: Optional system prompt to set context.
            temperature: Sampling temperature (0-1). Default 0.7.
            max_tokens: Maximum tokens to generate. None for model default.

        Returns:
            Generated text response.

        Raises:
            Exception: If generation fails.
        """
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        try:
            logger.debug(f"Generating response for prompt: {prompt[:50]}...")

            options = {"temperature": temperature}
            if max_tokens:
                options["num_predict"] = max_tokens

            response = self.client.chat(model=self.model, messages=messages, options=options)

            content = response.get("message", {}).get("content", "")
            logger.debug(f"Generated response of length {len(content)}")

            return content

        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise

    async def generate_stream(
        self, prompt: str, system: str | None = None, temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Generate a response with streaming.

        Args:
            prompt: The user's prompt/question.
            system: Optional system prompt to set context.
            temperature: Sampling temperature (0-1). Default 0.7.

        Yields:
            Chunks of generated text as they become available.
        """
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        try:
            logger.debug(f"Streaming response for prompt: {prompt[:50]}...")

            stream = self.client.chat(
                model=self.model,
                messages=messages,
                stream=True,
                options={"temperature": temperature},
            )

            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content

        except Exception as e:
            logger.error(f"Failed to stream response: {e}")
            raise

    async def check_health(self) -> bool:
        """Check if the LLM service is healthy.

        Returns:
            True if service is reachable and model is loaded.
        """
        try:
            # List models to check connection
            models = self.client.list()
            model_names = [m.get("name", "") for m in models.get("models", [])]

            # Check if our model is available
            if any(self.model in name for name in model_names):
                return True

            logger.warning(f"Model {self.model} not found in available models")
            return False

        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return False


# Global LLM client instance
llm_client = LLMClient()
