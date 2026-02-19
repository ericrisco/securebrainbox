"""Tests for agent module."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

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
        assert brain.soul_context is None

    @pytest.mark.asyncio
    async def test_brain_initialize(self, brain):
        """Test that brain can be initialized."""
        with (
            patch("src.agent.brain.vector_store") as mock_vs,
            patch("src.agent.brain.knowledge_graph"),
            patch("src.agent.brain.SoulInitializer") as mock_si,
            patch("src.agent.brain.SoulLoader") as mock_sl,
            patch("src.agent.brain.get_skill_registry") as mock_sr,
        ):
            mock_vs.connect = AsyncMock()
            mock_si_inst = MagicMock()
            mock_si_inst.initialize = AsyncMock()
            mock_si.return_value = mock_si_inst
            mock_sl_inst = MagicMock()
            mock_sl_inst.load = AsyncMock(return_value=MagicMock())
            mock_sl.return_value = mock_sl_inst
            mock_sr_inst = MagicMock()
            mock_sr.return_value = mock_sr_inst

            await brain.initialize()
            assert brain.initialized is True

    @pytest.mark.asyncio
    async def test_brain_initialize_idempotent(self, brain):
        """Test that multiple initializations are safe."""
        with (
            patch("src.agent.brain.vector_store") as mock_vs,
            patch("src.agent.brain.knowledge_graph"),
            patch("src.agent.brain.SoulInitializer") as mock_si,
            patch("src.agent.brain.SoulLoader") as mock_sl,
            patch("src.agent.brain.get_skill_registry") as mock_sr,
        ):
            mock_vs.connect = AsyncMock()
            mock_si_inst = MagicMock()
            mock_si_inst.initialize = AsyncMock()
            mock_si.return_value = mock_si_inst
            mock_sl_inst = MagicMock()
            mock_sl_inst.load = AsyncMock(return_value=MagicMock())
            mock_sl.return_value = mock_sl_inst
            mock_sr_inst = MagicMock()
            mock_sr.return_value = mock_sr_inst

            await brain.initialize()
            await brain.initialize()
            await brain.initialize()
            assert brain.initialized is True

    @pytest.mark.asyncio
    async def test_process_query_initializes(self, brain):
        """Test that process_query auto-initializes."""
        assert brain.initialized is False

        with (
            patch("src.agent.brain.vector_store") as mock_vs,
            patch("src.agent.brain.knowledge_graph"),
            patch("src.agent.brain.llm_client") as mock_llm,
            patch("src.agent.brain.SoulInitializer") as mock_si,
            patch("src.agent.brain.SoulLoader") as mock_sl,
            patch("src.agent.brain.get_skill_registry") as mock_sr,
        ):
            mock_vs.connect = AsyncMock()
            mock_vs.search = AsyncMock(return_value=[])
            mock_llm.generate = AsyncMock(return_value="AI response")
            mock_si_inst = MagicMock()
            mock_si_inst.initialize = AsyncMock()
            mock_si.return_value = mock_si_inst
            mock_sl_inst = MagicMock()
            mock_sl_inst.load = AsyncMock(return_value=MagicMock(is_empty=True))
            mock_sl.return_value = mock_sl_inst
            mock_sr_inst = MagicMock()
            mock_sr_inst.skills = []
            mock_sr.return_value = mock_sr_inst

            response = await brain.process_query("test query")

            assert brain.initialized is True
            assert response is not None
            assert len(response) > 0

    @pytest.mark.asyncio
    async def test_process_query_returns_string(self, brain):
        """Test that process_query returns a string response."""
        with (
            patch("src.agent.brain.vector_store") as mock_vs,
            patch("src.agent.brain.knowledge_graph"),
            patch("src.agent.brain.llm_client") as mock_llm,
            patch("src.agent.brain.SoulInitializer") as mock_si,
            patch("src.agent.brain.SoulLoader") as mock_sl,
            patch("src.agent.brain.get_skill_registry") as mock_sr,
        ):
            mock_vs.connect = AsyncMock()
            mock_vs.search = AsyncMock(return_value=[])
            mock_llm.generate = AsyncMock(return_value="Python is great")
            mock_si_inst = MagicMock()
            mock_si_inst.initialize = AsyncMock()
            mock_si.return_value = mock_si_inst
            mock_sl_inst = MagicMock()
            mock_sl_inst.load = AsyncMock(return_value=MagicMock(is_empty=True))
            mock_sl.return_value = mock_sl_inst
            mock_sr_inst = MagicMock()
            mock_sr_inst.skills = []
            mock_sr.return_value = mock_sr_inst

            response = await brain.process_query("What is Python?")

            assert isinstance(response, str)
            assert len(response) > 0

    @pytest.mark.asyncio
    async def test_index_text_returns_count(self, brain):
        """Test that index_text returns chunk count."""
        with (
            patch("src.agent.brain.vector_store") as mock_vs,
            patch("src.agent.brain.knowledge_graph"),
            patch("src.agent.brain.entity_extractor") as mock_ee,
            patch("src.agent.brain.SoulInitializer") as mock_si,
            patch("src.agent.brain.SoulLoader") as mock_sl,
            patch("src.agent.brain.get_skill_registry") as mock_sr,
        ):
            mock_vs.connect = AsyncMock()
            mock_vs.add_chunks_batch = AsyncMock(return_value=["id1"])
            mock_ee.extract = AsyncMock(
                return_value=MagicMock(error=None, entities=[], relations=[])
            )
            mock_si_inst = MagicMock()
            mock_si_inst.initialize = AsyncMock()
            mock_si.return_value = mock_si_inst
            mock_sl_inst = MagicMock()
            mock_sl_inst.load = AsyncMock(return_value=MagicMock())
            mock_sl.return_value = mock_sl_inst
            mock_sr_inst = MagicMock()
            mock_sr.return_value = mock_sr_inst

            result = await brain.index_text(
                text="This is test content",
                source="test.txt",
                source_type="text",
                metadata={"author": "test"},
            )

            assert isinstance(result, int)
            assert result > 0

    @pytest.mark.asyncio
    async def test_search_returns_list(self, brain):
        """Test that search returns a list."""
        with (
            patch("src.agent.brain.vector_store") as mock_vs,
            patch("src.agent.brain.knowledge_graph"),
            patch("src.agent.brain.SoulInitializer") as mock_si,
            patch("src.agent.brain.SoulLoader") as mock_sl,
            patch("src.agent.brain.get_skill_registry") as mock_sr,
        ):
            mock_vs.connect = AsyncMock()
            mock_vs.search = AsyncMock(return_value=[])
            mock_si_inst = MagicMock()
            mock_si_inst.initialize = AsyncMock()
            mock_si.return_value = mock_si_inst
            mock_sl_inst = MagicMock()
            mock_sl_inst.load = AsyncMock(return_value=MagicMock())
            mock_sl.return_value = mock_sl_inst
            mock_sr_inst = MagicMock()
            mock_sr.return_value = mock_sr_inst

            results = await brain.search("test query")
            assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_get_stats_returns_dict(self, brain):
        """Test that get_stats returns a dictionary."""
        with (
            patch("src.agent.brain.vector_store") as mock_vs,
            patch("src.agent.brain.knowledge_graph") as mock_kg,
            patch("src.agent.brain.SoulInitializer") as mock_si,
            patch("src.agent.brain.SoulLoader") as mock_sl,
            patch("src.agent.brain.get_skill_registry") as mock_sr,
        ):
            mock_vs.connect = AsyncMock()
            mock_vs.get_stats = AsyncMock(return_value={"total_chunks": 5})
            mock_kg.get_entity_count.return_value = 0
            mock_kg.get_relation_count.return_value = 0
            mock_si_inst = MagicMock()
            mock_si_inst.initialize = AsyncMock()
            mock_si.return_value = mock_si_inst
            mock_sl_inst = MagicMock()
            mock_sl_inst.load = AsyncMock(return_value=MagicMock())
            mock_sl.return_value = mock_sl_inst
            mock_sr_inst = MagicMock()
            mock_sr.return_value = mock_sr_inst

            stats = await brain.get_stats()
            assert isinstance(stats, dict)
            assert "total_chunks" in stats


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
