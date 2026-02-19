"""Tests for RAG functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestTextChunker:
    """Test text chunking functionality."""
    
    def test_chunk_empty_text(self):
        """Test chunking empty text returns empty list."""
        from src.utils.chunking import text_chunker
        
        result = text_chunker.chunk("")
        assert result == []
        
        result = text_chunker.chunk("   ")
        assert result == []
    
    def test_chunk_short_text(self):
        """Test chunking short text returns single chunk."""
        from src.utils.chunking import text_chunker
        
        short_text = "This is a short text."
        result = text_chunker.chunk(short_text)
        
        assert len(result) == 1
        assert result[0] == short_text
    
    def test_chunk_long_text(self):
        """Test chunking long text creates multiple chunks."""
        from src.utils.chunking import text_chunker
        
        # Create text longer than chunk_size
        long_text = "Lorem ipsum dolor sit amet. " * 100
        result = text_chunker.chunk(long_text)
        
        assert len(result) > 1
        # Each chunk should be within limits
        for chunk in result:
            assert len(chunk) <= 1200  # chunk_size + some buffer
    
    def test_chunk_with_metadata(self):
        """Test chunking with metadata."""
        from src.utils.chunking import text_chunker
        
        text = "This is test content for chunking."
        result = text_chunker.chunk_with_metadata(
            text=text,
            source="test.txt",
            source_type="text",
            extra_metadata={"author": "test"}
        )
        
        assert len(result) == 1
        assert result[0]["content"] == text
        assert result[0]["source"] == "test.txt"
        assert result[0]["source_type"] == "text"
        assert result[0]["chunk_index"] == 0
        assert result[0]["metadata"] == {"author": "test"}
    
    def test_estimate_chunks(self):
        """Test chunk estimation."""
        from src.utils.chunking import text_chunker
        
        # Empty text
        assert text_chunker.estimate_chunks("") == 0
        
        # Short text
        short_text = "Hello"
        assert text_chunker.estimate_chunks(short_text) == 1
        
        # Long text - should estimate multiple chunks
        long_text = "A" * 5000
        estimate = text_chunker.estimate_chunks(long_text)
        assert estimate > 1


class TestPrompts:
    """Test prompt templates."""
    
    def test_system_prompt_exists(self):
        """Test system prompt is defined."""
        from src.agent.prompts import SYSTEM_PROMPT
        
        assert SYSTEM_PROMPT is not None
        assert len(SYSTEM_PROMPT) > 0
        assert "SecureBrain" in SYSTEM_PROMPT
    
    def test_rag_template_has_placeholders(self):
        """Test RAG template has required placeholders."""
        from src.agent.prompts import RAG_PROMPT_TEMPLATE
        
        assert "{context}" in RAG_PROMPT_TEMPLATE
        assert "{query}" in RAG_PROMPT_TEMPLATE
    
    def test_indexing_confirmation_format(self):
        """Test indexing confirmation can be formatted."""
        from src.agent.prompts import INDEXING_CONFIRMATION
        
        result = INDEXING_CONFIRMATION.format(
            source="test.pdf",
            source_type="pdf",
            chunk_count=5
        )
        
        assert "test.pdf" in result
        assert "pdf" in result
        assert "5" in result


class TestEmbeddingClient:
    """Test embedding client (mocked)."""
    
    @pytest.mark.asyncio
    async def test_embed_returns_list(self):
        """Test embed returns a list of floats."""
        with patch('src.utils.embeddings.ollama.Client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.embeddings.return_value = {
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
            }
            mock_client.return_value = mock_instance
            
            from src.utils.embeddings import EmbeddingClient
            client = EmbeddingClient()
            client._client = mock_instance
            
            result = await client.embed("test text")
            
            assert isinstance(result, list)
            assert len(result) == 5
            assert all(isinstance(x, float) for x in result)


class TestLLMClient:
    """Test LLM client (mocked)."""
    
    @pytest.mark.asyncio
    async def test_generate_returns_string(self):
        """Test generate returns a string."""
        with patch('src.utils.llm.ollama.Client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.chat.return_value = {
                "message": {"content": "Generated response"}
            }
            mock_client.return_value = mock_instance
            
            from src.utils.llm import LLMClient
            client = LLMClient()
            client._client = mock_instance
            
            result = await client.generate("test prompt")
            
            assert isinstance(result, str)
            assert result == "Generated response"
    
    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self):
        """Test generate with system prompt."""
        with patch('src.utils.llm.ollama.Client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.chat.return_value = {
                "message": {"content": "Response"}
            }
            mock_client.return_value = mock_instance
            
            from src.utils.llm import LLMClient
            client = LLMClient()
            client._client = mock_instance
            
            await client.generate("prompt", system="You are helpful")
            
            # Verify chat was called with system message
            call_args = mock_instance.chat.call_args
            messages = call_args.kwargs.get('messages', call_args[1].get('messages', []))
            
            assert len(messages) == 2
            assert messages[0]["role"] == "system"


class TestSecureBrain:
    """Test SecureBrain agent (mocked)."""
    
    @pytest.fixture
    def mock_vector_store(self):
        """Mock the vector store."""
        with patch('src.agent.brain.vector_store') as mock:
            mock.connect = AsyncMock()
            mock.search = AsyncMock(return_value=[])
            mock.add_chunks_batch = AsyncMock(return_value=["id1", "id2"])
            mock.get_stats = AsyncMock(return_value={"total_chunks": 10})
            yield mock
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock the LLM client."""
        with patch('src.agent.brain.llm_client') as mock:
            mock.generate = AsyncMock(return_value="AI response")
            yield mock
    
    @pytest.mark.asyncio
    async def test_initialize(self, mock_vector_store):
        """Test agent initialization."""
        from src.agent.brain import SecureBrain
        
        brain = SecureBrain()
        assert not brain.initialized
        
        await brain.initialize()
        
        assert brain.initialized
        mock_vector_store.connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_query_no_context(self, mock_vector_store, mock_llm_client):
        """Test query processing with no context found."""
        from src.agent.brain import SecureBrain
        
        brain = SecureBrain()
        mock_vector_store.search.return_value = []
        
        result = await brain.process_query("What is Python?")
        
        assert isinstance(result, str)
        mock_llm_client.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_query_with_context(self, mock_vector_store, mock_llm_client):
        """Test query processing with context found."""
        from src.agent.brain import SecureBrain
        
        brain = SecureBrain()
        mock_vector_store.search.return_value = [
            {
                "content": "Python is a programming language",
                "source": "doc1.pdf",
                "source_type": "pdf",
                "distance": 0.1
            }
        ]
        
        result = await brain.process_query("What is Python?")
        
        assert isinstance(result, str)
        assert "doc1.pdf" in result or "Sources" in result
    
    @pytest.mark.asyncio
    async def test_index_text(self, mock_vector_store):
        """Test text indexing."""
        from src.agent.brain import SecureBrain
        
        brain = SecureBrain()
        
        count = await brain.index_text(
            text="This is test content for indexing.",
            source="test.txt",
            source_type="text"
        )
        
        assert count > 0
        mock_vector_store.add_chunks_batch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_stats(self, mock_vector_store):
        """Test getting statistics."""
        from src.agent.brain import SecureBrain
        
        brain = SecureBrain()
        
        stats = await brain.get_stats()
        
        assert "total_chunks" in stats
        assert stats["total_chunks"] == 10
