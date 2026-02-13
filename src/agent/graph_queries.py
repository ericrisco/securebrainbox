"""Graph query helpers and idea generation."""

import logging
import random
from dataclasses import dataclass
from typing import Optional

from src.storage.graph import knowledge_graph
from src.utils.llm import llm_client

logger = logging.getLogger(__name__)


@dataclass
class GraphStats:
    """Statistics about the knowledge graph."""
    entity_count: int
    relation_count: int
    most_connected: list[dict]


@dataclass
class CrazyIdea:
    """A creative idea based on graph connections."""
    path: list[str]
    idea: str
    explanation: str


IDEAS_PROMPT = """Generate a creative, practical idea connecting these concepts.

PATH: {path}

The path shows how these concepts are connected in the user's knowledge base.
Generate ONE specific, actionable idea that combines these concepts.

Respond with:
IDEA: [One sentence describing the idea]
EXPLANATION: [2-3 sentences explaining why this connection is interesting and how it could be useful]

Be creative but practical. Focus on what could actually be built or done."""


class GraphQueryHelper:
    """Helper for graph queries and idea generation."""
    
    async def get_stats(self) -> GraphStats:
        """Get knowledge graph statistics."""
        return GraphStats(
            entity_count=knowledge_graph.get_entity_count(),
            relation_count=knowledge_graph.get_relation_count(),
            most_connected=knowledge_graph.get_most_connected(5)
        )
    
    async def explore_entity(self, entity_name: str) -> dict:
        """Explore an entity and its connections.
        
        Args:
            entity_name: Entity to explore.
            
        Returns:
            Dict with entity info and connections.
        """
        # Search for matching entities
        matches = knowledge_graph.search_entities(entity_name, limit=1)
        
        if not matches:
            return {"found": False, "entity": entity_name}
        
        entity = matches[0]
        
        # Get related entities
        related = knowledge_graph.get_related_entities(entity["name"], depth=2, limit=15)
        
        # Get documents mentioning this entity
        documents = knowledge_graph.get_documents_for_entity(entity["name"], limit=5)
        
        return {
            "found": True,
            "entity": entity,
            "related": related,
            "documents": documents
        }
    
    async def generate_ideas(
        self,
        topic: str,
        count: int = 3
    ) -> list[CrazyIdea]:
        """Generate creative ideas based on graph connections.
        
        Args:
            topic: Starting topic/entity.
            count: Number of ideas to generate.
            
        Returns:
            List of creative ideas.
        """
        ideas = []
        
        # Find entities related to topic
        matches = knowledge_graph.search_entities(topic, limit=5)
        
        if not matches:
            logger.info(f"No matching entities for topic: {topic}")
            return []
        
        # For each match, explore second-degree connections
        for match in matches[:2]:
            related = knowledge_graph.get_related_entities(
                match["name"],
                depth=2,
                limit=10
            )
            
            if not related:
                continue
            
            # Sample random paths
            for _ in range(min(count, len(related))):
                target = random.choice(related)
                
                # Build a conceptual path
                path = [match["name"], "→", target["name"]]
                
                # Try to find actual path
                actual_path = knowledge_graph.find_path(match["name"], target["name"])
                if len(actual_path) > 2:
                    path = actual_path
                
                # Generate idea using LLM
                idea = await self._generate_single_idea(path)
                if idea:
                    ideas.append(idea)
                
                if len(ideas) >= count:
                    break
            
            if len(ideas) >= count:
                break
        
        return ideas[:count]
    
    async def _generate_single_idea(self, path: list[str]) -> Optional[CrazyIdea]:
        """Generate a single idea from a connection path."""
        try:
            path_str = " → ".join(path)
            prompt = IDEAS_PROMPT.format(path=path_str)
            
            response = await llm_client.generate(prompt, max_tokens=300)
            
            # Parse response
            idea_text = ""
            explanation = ""
            
            for line in response.split("\n"):
                line = line.strip()
                if line.startswith("IDEA:"):
                    idea_text = line[5:].strip()
                elif line.startswith("EXPLANATION:"):
                    explanation = line[12:].strip()
            
            if not idea_text:
                # Try to use the whole response
                idea_text = response.strip()[:200]
            
            return CrazyIdea(
                path=path,
                idea=idea_text,
                explanation=explanation
            )
            
        except Exception as e:
            logger.error(f"Failed to generate idea: {e}")
            return None
    
    async def find_connections(
        self,
        entity1: str,
        entity2: str
    ) -> dict:
        """Find how two entities are connected.
        
        Args:
            entity1: First entity name.
            entity2: Second entity name.
            
        Returns:
            Dict with connection info.
        """
        # Find path
        path = knowledge_graph.find_path(entity1, entity2)
        
        if path:
            return {
                "connected": True,
                "path": path,
                "distance": len(path) - 1
            }
        
        # No direct path - check if both exist
        e1_matches = knowledge_graph.search_entities(entity1, limit=1)
        e2_matches = knowledge_graph.search_entities(entity2, limit=1)
        
        return {
            "connected": False,
            "entity1_found": len(e1_matches) > 0,
            "entity2_found": len(e2_matches) > 0,
            "path": []
        }
    
    def format_graph_visualization(self, entity_name: str, related: list[dict]) -> str:
        """Format a simple ASCII visualization of entity connections.
        
        Args:
            entity_name: Central entity.
            related: List of related entities.
            
        Returns:
            ASCII art visualization.
        """
        if not related:
            return f"  [{entity_name}] (no connections)"
        
        lines = []
        lines.append(f"  [{entity_name}]")
        lines.append("       │")
        
        for i, rel in enumerate(related[:10]):
            prefix = "├──" if i < len(related) - 1 else "└──"
            type_emoji = self._get_type_emoji(rel.get("type", ""))
            lines.append(f"       {prefix} {type_emoji} {rel['name']}")
        
        if len(related) > 10:
            lines.append(f"       └── ... and {len(related) - 10} more")
        
        return "\n".join(lines)
    
    def _get_type_emoji(self, entity_type: str) -> str:
        """Get emoji for entity type."""
        return {
            "PERSON": "👤",
            "ORG": "🏢",
            "TECHNOLOGY": "⚙️",
            "CONCEPT": "💡",
            "LOCATION": "📍",
            "DATE": "📅",
        }.get(entity_type.upper(), "•")


# Global instance
graph_helper = GraphQueryHelper()
