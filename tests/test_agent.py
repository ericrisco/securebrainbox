"""Tests for agent module."""

from datetime import datetime

import pytest

from src.agent.brain import IndexedContent, SecureBrain


class TestSecureBrain:
    """Test SecureBrain agent."""

    @pytest.fixture
    def brain(self):
        """Create a fresh SecureBrain instance."""
        return SecureBrain()

    def test_brain_initial_state(self, brain):
        """Test that brain starts uninitialized."""
        assert brain.initialized is False
        assert brain._ollama_client is None
        assert brain._weaviate_client is None

    @pytest.mark.asyncio
    async def test_brain_initialize(self, brain):
        """Test that brain can be initialized."""
        await brain.initialize()

        assert brain.initialized is True

    @pytest.mark.asyncio
    async def test_brain_initialize_idempotent(self, brain):
        """Test that multiple initializations are safe."""
        await brain.initialize()
        await brain.initialize()
        await brain.initialize()

        assert brain.initialized is True

    @pytest.mark.asyncio
    async def test_process_query_initializes(self, brain):
        """Test that process_query auto-initializes."""
        assert brain.initialized is False

        response = await brain.process_query("test query")

        assert brain.initialized is True
        assert response is not None
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_process_query_returns_string(self, brain):
        """Test that process_query returns a string response."""
        response = await brain.process_query("What is Python?")

        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_index_content_returns_indexed_content(self, brain):
        """Test that index_content returns IndexedContent."""
        result = await brain.index_content(
            content="This is test content",
            source="test.txt",
            source_type="text",
            metadata={"author": "test"},
        )

        assert isinstance(result, IndexedContent)
        assert result.source == "test.txt"
        assert result.source_type == "text"
        assert result.metadata == {"author": "test"}
        assert isinstance(result.indexed_at, datetime)

    @pytest.mark.asyncio
    async def test_search_returns_list(self, brain):
        """Test that search returns a list."""
        results = await brain.search("test query")

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_get_stats_returns_dict(self, brain):
        """Test that get_stats returns a dictionary."""
        stats = await brain.get_stats()

        assert isinstance(stats, dict)
        assert "documents" in stats
        assert "chunks" in stats


class TestIndexedContent:
    """Test IndexedContent dataclass."""

    def test_indexed_content_creation(self):
        """Test creating IndexedContent."""
        content = IndexedContent(
            content_id="test123",
            source="document.pdf",
            source_type="pdf",
            chunk_count=5,
            indexed_at=datetime.now(),
            metadata={"pages": 10},
        )

        assert content.content_id == "test123"
        assert content.source == "document.pdf"
        assert content.source_type == "pdf"
        assert content.chunk_count == 5
        assert content.metadata == {"pages": 10}
