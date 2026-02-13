"""Main agent brain with RAG capabilities.

This module contains the SecureBrain class which orchestrates all AI
operations including query processing, content indexing, and response
generation using RAG (Retrieval-Augmented Generation).
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.config import settings
from src.storage.vectors import vector_store
from src.storage.graph import knowledge_graph
from src.utils.llm import llm_client
from src.utils.chunking import text_chunker
from src.agent.prompts import (
    SYSTEM_PROMPT,
    RAG_PROMPT_TEMPLATE,
    NO_CONTEXT_PROMPT,
    INDEXING_CONFIRMATION,
)
from src.agent.entities import entity_extractor

logger = logging.getLogger(__name__)


@dataclass
class IndexedContent:
    """Represents indexed content in the knowledge base."""
    
    content_id: str
    source: str
    source_type: str
    chunk_count: int
    indexed_at: datetime
    metadata: dict


@dataclass 
class SearchResult:
    """Represents a search result from the knowledge base."""
    
    content: str
    source: str
    source_type: str
    relevance: float
    chunk_index: int


class SecureBrain:
    """Main agent that orchestrates all AI operations.
    
    This is the central brain of SecureBrainBox. It handles:
    - Processing user queries using RAG
    - Indexing new content into the knowledge base
    - Searching the knowledge base
    - Generating creative ideas
    
    Attributes:
        initialized: Whether the agent has been initialized.
    """
    
    def __init__(self):
        """Initialize the SecureBrain agent."""
        self.initialized = False
        logger.info("SecureBrain instance created")
    
    async def initialize(self) -> None:
        """Initialize connections to AI services.
        
        Sets up connections to Weaviate vector store.
        Called automatically on first operation if not already initialized.
        """
        if self.initialized:
            return
        
        logger.info("Initializing SecureBrain...")
        logger.info(f"  Ollama: {settings.ollama_host}")
        logger.info(f"  Weaviate: {settings.weaviate_host}")
        logger.info(f"  LLM Model: {settings.ollama_model}")
        logger.info(f"  Embed Model: {settings.ollama_embed_model}")
        
        try:
            # Connect to vector store
            await vector_store.connect()
            
            # Connect to knowledge graph
            knowledge_graph.connect()
            
            self.initialized = True
            logger.info("SecureBrain initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SecureBrain: {e}")
            raise
    
    async def process_query(self, query: str) -> str:
        """Process a user query using RAG.
        
        Searches the knowledge base for relevant context, then uses
        the LLM to generate a response based on that context.
        
        Args:
            query: The user's question or message.
            
        Returns:
            AI-generated response string.
        """
        if not self.initialized:
            await self.initialize()
        
        logger.info(f"Processing query: {query[:50]}...")
        
        try:
            # 1. Search for relevant context
            results = await vector_store.search(query, limit=5)
            
            if not results:
                # No context found - use the no-context prompt
                logger.debug("No relevant context found, using general response")
                prompt = NO_CONTEXT_PROMPT.format(query=query)
                return await llm_client.generate(
                    prompt=prompt,
                    system=SYSTEM_PROMPT
                )
            
            # 2. Build context from results
            context_parts = []
            sources = set()
            
            for r in results:
                source_name = r.get("source", "unknown")
                content = r.get("content", "")
                context_parts.append(f"[Source: {source_name}]\n{content}")
                sources.add(source_name)
            
            context = "\n\n---\n\n".join(context_parts)
            
            # 3. Generate response with context
            prompt = RAG_PROMPT_TEMPLATE.format(
                context=context,
                query=query
            )
            
            response = await llm_client.generate(
                prompt=prompt,
                system=SYSTEM_PROMPT
            )
            
            # 4. Add sources footer if we have sources
            if sources and len(sources) <= 5:
                source_list = ", ".join(f"`{s}`" for s in sorted(sources))
                response += f"\n\n📚 _Sources: {source_list}_"
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return (
                "❌ Sorry, I encountered an error processing your question. "
                "Please check if the AI services are running with `/status`."
            )
    
    async def index_text(
        self,
        text: str,
        source: str,
        source_type: str = "text",
        metadata: Optional[dict] = None
    ) -> int:
        """Index text content into the knowledge base.
        
        Chunks the text and stores each chunk with its embedding
        in the vector store.
        
        Args:
            text: The text content to index.
            source: Source identifier (filename, URL, etc.).
            source_type: Type of content (text, pdf, image, audio, url).
            metadata: Optional additional metadata.
            
        Returns:
            Number of chunks indexed.
        """
        if not self.initialized:
            await self.initialize()
        
        logger.info(f"Indexing content from {source} ({source_type})")
        logger.info(f"  Content length: {len(text)} chars")
        
        try:
            # Chunk the text
            chunks = text_chunker.chunk(text)
            
            if not chunks:
                logger.warning(f"No chunks generated from {source}")
                return 0
            
            # Index each chunk
            chunk_dicts = [
                {"content": chunk, "metadata": metadata}
                for chunk in chunks
            ]
            
            await vector_store.add_chunks_batch(
                chunks=chunk_dicts,
                source=source,
                source_type=source_type
            )
            
            logger.info(f"Indexed {len(chunks)} chunks from {source}")
            
            # Extract entities and add to knowledge graph
            await self._extract_and_add_entities(text, source, source_type)
            
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error indexing content: {e}")
            raise
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        source_type: Optional[str] = None
    ) -> list[SearchResult]:
        """Search the knowledge base.
        
        Args:
            query: Search query string.
            limit: Maximum number of results.
            source_type: Filter by source type (optional).
            
        Returns:
            List of SearchResult objects.
        """
        if not self.initialized:
            await self.initialize()
        
        logger.info(f"Searching: {query[:50]}...")
        
        results = await vector_store.search(
            query=query,
            limit=limit,
            source_type=source_type
        )
        
        return [
            SearchResult(
                content=r["content"],
                source=r["source"],
                source_type=r["source_type"],
                relevance=1 - r.get("distance", 0),  # Convert distance to relevance
                chunk_index=r.get("chunk_index", 0)
            )
            for r in results
        ]
    
    async def _extract_and_add_entities(
        self,
        text: str,
        source: str,
        source_type: str
    ) -> None:
        """Extract entities from text and add to knowledge graph.
        
        Args:
            text: Text to extract entities from.
            source: Source identifier.
            source_type: Type of content.
        """
        try:
            # Extract entities using LLM
            result = await entity_extractor.extract(text)
            
            if result.error:
                logger.warning(f"Entity extraction failed: {result.error}")
                return
            
            if not result.entities:
                logger.debug(f"No entities found in {source}")
                return
            
            # Add document node
            knowledge_graph.add_document(
                source=source,
                source_type=source_type,
                timestamp=int(time.time())
            )
            
            # Add entities and mentions
            for entity in result.entities:
                knowledge_graph.add_entity(
                    name=entity.name,
                    entity_type=entity.type,
                    description=entity.description,
                    source=source
                )
                knowledge_graph.add_mention(source, entity.name)
            
            # Add relations between entities
            for rel in result.relations:
                knowledge_graph.add_relation(
                    from_entity=rel.from_entity,
                    to_entity=rel.to_entity,
                    relation=rel.relation
                )
            
            logger.info(
                f"Added {len(result.entities)} entities and "
                f"{len(result.relations)} relations from {source}"
            )
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
    
    async def get_stats(self) -> dict:
        """Get knowledge base statistics.
        
        Returns:
            Dictionary with stats like chunk count.
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            stats = await vector_store.get_stats()
            return {
                "total_chunks": stats.get("total_chunks", 0),
                "collection": stats.get("collection", "Knowledge"),
                "entities": knowledge_graph.get_entity_count(),
                "relations": knowledge_graph.get_relation_count(),
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_chunks": 0, "error": str(e)}
    
    def get_indexing_confirmation(
        self,
        source: str,
        source_type: str,
        chunk_count: int
    ) -> str:
        """Generate an indexing confirmation message.
        
        Args:
            source: Source that was indexed.
            source_type: Type of content.
            chunk_count: Number of chunks created.
            
        Returns:
            Formatted confirmation message.
        """
        return INDEXING_CONFIRMATION.format(
            source=source,
            source_type=source_type,
            chunk_count=chunk_count
        )


# Global agent instance
agent = SecureBrain()
