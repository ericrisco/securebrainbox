"""Tests for knowledge graph functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.processors.base import ProcessedContent


class TestEntityExtraction:
    """Test entity extraction."""
    
    def test_extraction_prompt_format(self):
        """Test extraction prompt is properly formatted."""
        from src.agent.entities import EXTRACTION_PROMPT
        
        # Check prompt has required placeholders
        assert "{text}" in EXTRACTION_PROMPT
        
        # Check it mentions entity types
        assert "PERSON" in EXTRACTION_PROMPT
        assert "ORG" in EXTRACTION_PROMPT
        assert "TECHNOLOGY" in EXTRACTION_PROMPT
    
    def test_extracted_entity_dataclass(self):
        """Test ExtractedEntity dataclass."""
        from src.agent.entities import ExtractedEntity
        
        entity = ExtractedEntity(
            name="Python",
            type="TECHNOLOGY",
            description="Programming language"
        )
        
        assert entity.name == "Python"
        assert entity.type == "TECHNOLOGY"
        assert entity.description == "Programming language"
    
    def test_extraction_result_dataclass(self):
        """Test ExtractionResult dataclass."""
        from src.agent.entities import ExtractionResult, ExtractedEntity, ExtractedRelation
        
        result = ExtractionResult(
            entities=[ExtractedEntity("Python", "TECHNOLOGY")],
            relations=[ExtractedRelation("Python", "Django", "USES")]
        )
        
        assert len(result.entities) == 1
        assert len(result.relations) == 1
        assert result.error is None
    
    def test_normalize_name(self):
        """Test entity name normalization."""
        from src.agent.entities import EntityExtractor
        
        extractor = EntityExtractor()
        
        assert extractor._normalize_name("  python  ") == "Python"
        assert extractor._normalize_name("OPENAI") == "Openai"
        assert extractor._normalize_name("machine learning") == "Machine Learning"


class TestKnowledgeGraph:
    """Test knowledge graph operations."""
    
    def test_graph_schema_constants(self):
        """Test that graph has expected node/edge types."""
        from src.storage.graph import KnowledgeGraph
        
        graph = KnowledgeGraph()
        
        # Check class exists and has key methods
        assert hasattr(graph, "add_entity")
        assert hasattr(graph, "add_document")
        assert hasattr(graph, "add_mention")
        assert hasattr(graph, "add_relation")
    
    def test_query_methods_exist(self):
        """Test query methods exist."""
        from src.storage.graph import KnowledgeGraph
        
        graph = KnowledgeGraph()
        
        assert hasattr(graph, "get_related_entities")
        assert hasattr(graph, "find_path")
        assert hasattr(graph, "get_documents_for_entity")
        assert hasattr(graph, "get_most_connected")
        assert hasattr(graph, "search_entities")


class TestGraphQueryHelper:
    """Test graph query helper."""
    
    def test_helper_has_methods(self):
        """Test helper has required methods."""
        from src.agent.graph_queries import GraphQueryHelper
        
        helper = GraphQueryHelper()
        
        assert hasattr(helper, "get_stats")
        assert hasattr(helper, "explore_entity")
        assert hasattr(helper, "generate_ideas")
        assert hasattr(helper, "find_connections")
    
    def test_format_graph_visualization(self):
        """Test ASCII visualization formatting."""
        from src.agent.graph_queries import GraphQueryHelper
        
        helper = GraphQueryHelper()
        
        # Empty related list
        result = helper.format_graph_visualization("Python", [])
        assert "[Python]" in result
        assert "no connections" in result
        
        # With related entities
        related = [
            {"name": "Django", "type": "TECHNOLOGY"},
            {"name": "Flask", "type": "TECHNOLOGY"},
        ]
        result = helper.format_graph_visualization("Python", related)
        
        assert "[Python]" in result
        assert "Django" in result
        assert "Flask" in result
    
    def test_type_emoji_mapping(self):
        """Test entity type to emoji mapping."""
        from src.agent.graph_queries import GraphQueryHelper
        
        helper = GraphQueryHelper()
        
        assert helper._get_type_emoji("PERSON") == "👤"
        assert helper._get_type_emoji("ORG") == "🏢"
        assert helper._get_type_emoji("TECHNOLOGY") == "⚙️"
        assert helper._get_type_emoji("UNKNOWN") == "•"


class TestCrazyIdeas:
    """Test crazy ideas generation."""
    
    def test_crazy_idea_dataclass(self):
        """Test CrazyIdea dataclass."""
        from src.agent.graph_queries import CrazyIdea
        
        idea = CrazyIdea(
            path=["Python", "Django", "Web"],
            idea="Build a web scraper with Django admin",
            explanation="Combines Python's power with Django's admin interface"
        )
        
        assert len(idea.path) == 3
        assert "web" in idea.idea.lower()
        assert idea.explanation != ""
    
    def test_ideas_prompt_format(self):
        """Test ideas prompt is properly formatted."""
        from src.agent.graph_queries import IDEAS_PROMPT
        
        assert "{path}" in IDEAS_PROMPT
        assert "IDEA:" in IDEAS_PROMPT
        assert "EXPLANATION:" in IDEAS_PROMPT


class TestBrainGraphIntegration:
    """Test brain integration with graph."""
    
    def test_brain_imports_graph(self):
        """Test brain imports graph components."""
        from src.agent.brain import SecureBrain
        
        # Check imports work
        from src.storage.graph import knowledge_graph
        from src.agent.entities import entity_extractor
        
        assert knowledge_graph is not None
        assert entity_extractor is not None
    
    def test_brain_has_entity_extraction_method(self):
        """Test brain has entity extraction method."""
        from src.agent.brain import SecureBrain
        
        brain = SecureBrain()
        
        assert hasattr(brain, "_extract_and_add_entities")


class TestGraphCommands:
    """Test graph-related bot commands."""
    
    def test_commands_imported(self):
        """Test graph commands are imported in app."""
        from src.bot.commands import graph_command, ideas_command
        
        assert callable(graph_command)
        assert callable(ideas_command)
    
    def test_commands_registered(self):
        """Test commands would be registered."""
        from src.bot.app import graph_command, ideas_command
        
        assert graph_command is not None
        assert ideas_command is not None
