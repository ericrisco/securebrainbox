"""Weaviate vector store interface."""

import json
import logging
from datetime import datetime
from urllib.parse import urlparse

import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.query import MetadataQuery

from src.config import settings
from src.utils.embeddings import embedding_client

logger = logging.getLogger(__name__)


class VectorStore:
    """Weaviate vector store for the knowledge base.

    Handles storage and retrieval of document chunks with their
    embeddings for semantic search.

    Attributes:
        client: Weaviate client instance.
        collection: The main knowledge collection.
    """

    COLLECTION_NAME = "Knowledge"

    def __init__(self):
        """Initialize the vector store."""
        self._client: weaviate.WeaviateClient | None = None
        self._collection = None
        self._connected = False
        logger.info("VectorStore initialized")

    @property
    def is_connected(self) -> bool:
        """Check if connected to Weaviate."""
        return self._connected and self._client is not None

    async def connect(self) -> None:
        """Connect to Weaviate and initialize schema.

        Creates the Knowledge collection if it doesn't exist.
        """
        if self._connected:
            logger.debug("Already connected to Weaviate")
            return

        logger.info(f"Connecting to Weaviate at {settings.weaviate_host}")

        # Parse host URL
        parsed = urlparse(settings.weaviate_host)
        host = parsed.hostname or "localhost"
        port = parsed.port or 8080

        try:
            self._client = weaviate.connect_to_local(
                host=host,
                port=port,
            )

            # Create collection if not exists
            if not self._client.collections.exists(self.COLLECTION_NAME):
                logger.info(f"Creating collection: {self.COLLECTION_NAME}")

                self._client.collections.create(
                    name=self.COLLECTION_NAME,
                    vectorizer_config=Configure.Vectorizer.none(),
                    properties=[
                        Property(
                            name="content",
                            data_type=DataType.TEXT,
                            description="The chunk content"
                        ),
                        Property(
                            name="source",
                            data_type=DataType.TEXT,
                            description="Source identifier"
                        ),
                        Property(
                            name="source_type",
                            data_type=DataType.TEXT,
                            description="Type of source (text, pdf, url, etc.)"
                        ),
                        Property(
                            name="chunk_index",
                            data_type=DataType.INT,
                            description="Index of chunk within document"
                        ),
                        Property(
                            name="total_chunks",
                            data_type=DataType.INT,
                            description="Total chunks in document"
                        ),
                        Property(
                            name="metadata_json",
                            data_type=DataType.TEXT,
                            description="Additional metadata as JSON"
                        ),
                        Property(
                            name="indexed_at",
                            data_type=DataType.TEXT,
                            description="Timestamp when indexed"
                        ),
                    ]
                )
                logger.info(f"Created collection: {self.COLLECTION_NAME}")

            self._collection = self._client.collections.get(self.COLLECTION_NAME)
            self._connected = True
            logger.info("Weaviate connected and ready")

        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise

    async def add_chunk(
        self,
        content: str,
        source: str,
        source_type: str,
        chunk_index: int = 0,
        total_chunks: int = 1,
        metadata: dict | None = None
    ) -> str:
        """Add a document chunk to the vector store.

        Args:
            content: The chunk text content.
            source: Source identifier (filename, URL, etc.).
            source_type: Type of source (text, pdf, url, etc.).
            chunk_index: Index of this chunk (0-indexed).
            total_chunks: Total number of chunks in the document.
            metadata: Additional metadata dict.

        Returns:
            UUID of the inserted object.
        """
        if not self.is_connected:
            await self.connect()

        # Generate embedding
        embedding = await embedding_client.embed(content)

        # Prepare properties
        properties = {
            "content": content,
            "source": source,
            "source_type": source_type,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
            "metadata_json": json.dumps(metadata or {}),
            "indexed_at": datetime.utcnow().isoformat(),
        }

        # Insert into Weaviate
        result = self._collection.data.insert(
            properties=properties,
            vector=embedding
        )

        logger.debug(f"Added chunk: {source} [{chunk_index}/{total_chunks}]")
        return str(result)

    async def add_chunks_batch(
        self,
        chunks: list[dict],
        source: str,
        source_type: str
    ) -> list[str]:
        """Add multiple chunks in a batch.

        Args:
            chunks: List of dicts with 'content' and optional 'metadata'.
            source: Source identifier.
            source_type: Type of source.

        Returns:
            List of UUIDs for inserted objects.
        """
        if not self.is_connected:
            await self.connect()

        ids = []
        total = len(chunks)

        for i, chunk in enumerate(chunks):
            chunk_id = await self.add_chunk(
                content=chunk["content"],
                source=source,
                source_type=source_type,
                chunk_index=i,
                total_chunks=total,
                metadata=chunk.get("metadata")
            )
            ids.append(chunk_id)

        logger.info(f"Added {len(ids)} chunks from {source}")
        return ids

    async def search(
        self,
        query: str,
        limit: int = 5,
        source_type: str | None = None,
        min_certainty: float = 0.0
    ) -> list[dict]:
        """Search for similar documents.

        Args:
            query: Search query string.
            limit: Maximum number of results.
            source_type: Filter by source type (optional).
            min_certainty: Minimum certainty threshold (0-1).

        Returns:
            List of matching documents with content and metadata.
        """
        if not self.is_connected:
            await self.connect()

        # Generate query embedding
        query_embedding = await embedding_client.embed(query)

        # Build query
        response = self._collection.query.near_vector(
            near_vector=query_embedding,
            limit=limit,
            return_metadata=MetadataQuery(distance=True, certainty=True)
        )

        results = []
        for obj in response.objects:
            # Filter by certainty if needed
            certainty = obj.metadata.certainty or 0
            if certainty < min_certainty:
                continue

            # Filter by source_type if specified
            if source_type and obj.properties.get("source_type") != source_type:
                continue

            results.append({
                "content": obj.properties.get("content", ""),
                "source": obj.properties.get("source", ""),
                "source_type": obj.properties.get("source_type", ""),
                "chunk_index": obj.properties.get("chunk_index", 0),
                "distance": obj.metadata.distance,
                "certainty": certainty,
                "metadata": json.loads(obj.properties.get("metadata_json", "{}")),
            })

        logger.debug(f"Search returned {len(results)} results for: {query[:30]}...")
        return results

    async def get_stats(self) -> dict:
        """Get statistics about the vector store.

        Returns:
            Dict with total_chunks and other stats.
        """
        if not self.is_connected:
            await self.connect()

        try:
            aggregate = self._collection.aggregate.over_all(total_count=True)
            return {
                "total_chunks": aggregate.total_count or 0,
                "collection": self.COLLECTION_NAME,
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"total_chunks": 0, "error": str(e)}

    async def delete_by_source(self, source: str) -> int:
        """Delete all chunks from a specific source.

        Args:
            source: Source identifier to delete.

        Returns:
            Number of deleted objects.
        """
        if not self.is_connected:
            await self.connect()

        # Note: Weaviate batch delete would be used here
        # For now, this is a placeholder
        logger.info(f"Would delete all chunks from source: {source}")
        return 0

    async def close(self) -> None:
        """Close the connection to Weaviate."""
        if self._client:
            self._client.close()
            self._connected = False
            logger.info("Weaviate connection closed")


# Global vector store instance
vector_store = VectorStore()
