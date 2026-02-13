"""Entity extraction using LLM."""

import json
import logging
from dataclasses import dataclass, field

from src.utils.llm import llm_client

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """Extracted entity from text."""
    name: str
    type: str  # PERSON, ORG, CONCEPT, TECHNOLOGY, LOCATION, DATE
    description: str = ""


@dataclass
class ExtractedRelation:
    """Extracted relation between entities."""
    from_entity: str
    to_entity: str
    relation: str  # RELATED_TO, WORKS_AT, CREATED_BY, USES, etc.


@dataclass
class ExtractionResult:
    """Result of entity extraction."""
    entities: list[ExtractedEntity] = field(default_factory=list)
    relations: list[ExtractedRelation] = field(default_factory=list)
    error: str | None = None


EXTRACTION_PROMPT = """Extract entities and relationships from the following text.

ENTITY TYPES:
- PERSON: People mentioned by name
- ORG: Companies, organizations, institutions
- TECHNOLOGY: Programming languages, frameworks, tools, libraries
- CONCEPT: Technical concepts, methodologies, ideas
- LOCATION: Places, countries, cities
- DATE: Specific dates or time periods

RELATIONSHIP TYPES:
- RELATED_TO: General relationship
- CREATED_BY: Something was created/founded by someone
- WORKS_AT: Person works at organization
- USES: Something uses/depends on something else
- PART_OF: Something is part of something larger

TEXT:
{text}

Respond ONLY with valid JSON in this exact format:
{{
  "entities": [
    {{"name": "entity name", "type": "TYPE", "description": "brief description"}}
  ],
  "relations": [
    {{"from": "entity1 name", "to": "entity2 name", "relation": "RELATION_TYPE"}}
  ]
}}

Rules:
- Normalize entity names (e.g., "Python" not "python language" or "Python programming")
- Only extract clearly mentioned entities
- Keep descriptions brief (max 20 words)
- Only include confident relations
- Return empty arrays if no entities found"""


class EntityExtractor:
    """Extract entities and relations from text using LLM."""

    def __init__(self, max_text_length: int = 4000):
        """Initialize extractor.

        Args:
            max_text_length: Max characters to process per call.
        """
        self.max_text_length = max_text_length

    async def extract(self, text: str) -> ExtractionResult:
        """Extract entities and relations from text.

        Args:
            text: Text to analyze.

        Returns:
            ExtractionResult with entities and relations.
        """
        if not text or len(text.strip()) < 10:
            return ExtractionResult()

        # Truncate if too long
        if len(text) > self.max_text_length:
            text = text[:self.max_text_length] + "..."
            logger.debug(f"Text truncated to {self.max_text_length} chars for extraction")

        try:
            prompt = EXTRACTION_PROMPT.format(text=text)
            response = await llm_client.generate(prompt, max_tokens=1500)

            # Parse JSON response
            return self._parse_response(response)

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return ExtractionResult(error=str(e))

    def _parse_response(self, response: str) -> ExtractionResult:
        """Parse LLM response into ExtractionResult."""
        try:
            # Clean response - find JSON block
            response = response.strip()

            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            # Find JSON object
            start = response.find("{")
            end = response.rfind("}") + 1

            if start == -1 or end == 0:
                logger.warning("No JSON found in extraction response")
                return ExtractionResult()

            json_str = response[start:end]
            data = json.loads(json_str)

            # Parse entities
            entities = []
            for e in data.get("entities", []):
                if e.get("name") and e.get("type"):
                    entities.append(ExtractedEntity(
                        name=self._normalize_name(e["name"]),
                        type=e["type"].upper(),
                        description=e.get("description", "")[:100]
                    ))

            # Parse relations
            relations = []
            for r in data.get("relations", []):
                if r.get("from") and r.get("to"):
                    relations.append(ExtractedRelation(
                        from_entity=self._normalize_name(r["from"]),
                        to_entity=self._normalize_name(r["to"]),
                        relation=r.get("relation", "RELATED_TO").upper()
                    ))

            return ExtractionResult(entities=entities, relations=relations)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse extraction JSON: {e}")
            return ExtractionResult(error="Invalid JSON response")
        except Exception as e:
            logger.warning(f"Failed to parse extraction: {e}")
            return ExtractionResult(error=str(e))

    def _normalize_name(self, name: str) -> str:
        """Normalize entity name."""
        # Remove extra whitespace
        name = " ".join(name.split())

        # Capitalize properly
        if name.isupper() or name.islower():
            name = name.title()

        return name[:100]  # Limit length


# Global instance
entity_extractor = EntityExtractor()
