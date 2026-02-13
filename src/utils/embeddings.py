"""Embedding generation using Ollama."""

import logging

import ollama

from src.config import settings

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Client for generating embeddings via Ollama.

    Uses the configured embedding model to generate vector representations
    of text for semantic search.

    Attributes:
        client: Ollama client instance.
        model: Name of the embedding model to use.
    """

    def __init__(self, host: str | None = None, model: str | None = None):
        """Initialize the embedding client.

        Args:
            host: Ollama server URL. Defaults to settings.ollama_host.
            model: Embedding model name. Defaults to settings.ollama_embed_model.
        """
        self.host = host or settings.ollama_host
        self.model = model or settings.ollama_embed_model
        self._client: ollama.Client | None = None
        logger.info(f"EmbeddingClient initialized with model: {self.model}")

    @property
    def client(self) -> ollama.Client:
        """Lazy initialization of Ollama client."""
        if self._client is None:
            self._client = ollama.Client(host=self.host)
        return self._client

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            List of floats representing the embedding vector.

        Raises:
            Exception: If embedding generation fails.
        """
        try:
            response = self.client.embeddings(model=self.model, prompt=text)
            embedding = response.get("embedding", [])
            logger.debug(f"Generated embedding of dimension {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.
        """
        embeddings = []
        for i, text in enumerate(texts):
            embedding = await self.embed(text)
            embeddings.append(embedding)
            if (i + 1) % 10 == 0:
                logger.debug(f"Generated {i + 1}/{len(texts)} embeddings")

        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings

    def get_dimension(self) -> int:
        """Get the embedding dimension by generating a test embedding.

        Returns:
            Dimension of embeddings for the current model.
        """
        import asyncio

        embedding = asyncio.get_event_loop().run_until_complete(self.embed("test"))
        return len(embedding)


# Global embedding client instance
embedding_client = EmbeddingClient()
