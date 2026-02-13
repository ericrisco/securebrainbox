"""Knowledge Graph storage using Kuzu embedded database."""

import logging
from pathlib import Path

import kuzu

from src.config import settings

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """Knowledge Graph using Kuzu embedded database.

    Schema:
    - Entity: name, type, description, source
    - Document: source, source_type, timestamp
    - MENTIONS: Document -> Entity
    - RELATED_TO: Entity <-> Entity
    """

    def __init__(self, db_path: str | None = None):
        """Initialize Kuzu database.

        Args:
            db_path: Path to database directory.
        """
        self.db_path = Path(db_path or settings.data_dir) / "kuzu_db"
        self.db_path.mkdir(parents=True, exist_ok=True)

        self._db: kuzu.Database | None = None
        self._conn: kuzu.Connection | None = None

    def connect(self) -> None:
        """Connect to Kuzu database and create schema."""
        logger.info(f"Connecting to Kuzu at {self.db_path}")

        self._db = kuzu.Database(str(self.db_path))
        self._conn = kuzu.Connection(self._db)

        self._init_schema()
        logger.info("Kuzu connected and schema initialized")

    def _init_schema(self) -> None:
        """Initialize graph schema if not exists."""
        # Node tables
        self._safe_execute("""
            CREATE NODE TABLE IF NOT EXISTS Entity (
                name STRING,
                type STRING,
                description STRING,
                source STRING,
                PRIMARY KEY (name)
            )
        """)

        self._safe_execute("""
            CREATE NODE TABLE IF NOT EXISTS Document (
                source STRING,
                source_type STRING,
                timestamp INT64,
                PRIMARY KEY (source)
            )
        """)

        # Relationship tables
        self._safe_execute("""
            CREATE REL TABLE IF NOT EXISTS MENTIONS (
                FROM Document TO Entity
            )
        """)

        self._safe_execute("""
            CREATE REL TABLE IF NOT EXISTS RELATED_TO (
                FROM Entity TO Entity,
                relation STRING
            )
        """)

    def _safe_execute(self, query: str, params: dict = None) -> kuzu.QueryResult | None:
        """Execute query with error handling."""
        try:
            if params:
                return self._conn.execute(query, params)
            return self._conn.execute(query)
        except Exception as e:
            # Ignore "already exists" errors
            if "already exists" in str(e).lower():
                return None
            logger.error(f"Kuzu query error: {e}")
            raise

    # --- Entity Operations ---

    def add_entity(
        self,
        name: str,
        entity_type: str,
        description: str = "",
        source: str = ""
    ) -> bool:
        """Add or update an entity.

        Args:
            name: Entity name (unique identifier).
            entity_type: Type (PERSON, ORG, CONCEPT, etc.).
            description: Brief description.
            source: Where this entity was found.

        Returns:
            True if successful.
        """
        try:
            # Try to merge (upsert)
            self._conn.execute(
                """
                MERGE (e:Entity {name: $name})
                ON CREATE SET e.type = $type, e.description = $desc, e.source = $source
                ON MATCH SET e.description = CASE WHEN $desc <> '' THEN $desc ELSE e.description END
                """,
                {"name": name, "type": entity_type, "desc": description, "source": source}
            )
            return True
        except Exception as e:
            logger.error(f"Error adding entity {name}: {e}")
            return False

    def add_document(
        self,
        source: str,
        source_type: str,
        timestamp: int = 0
    ) -> bool:
        """Add a document node."""
        try:
            self._conn.execute(
                """
                MERGE (d:Document {source: $source})
                ON CREATE SET d.source_type = $type, d.timestamp = $ts
                """,
                {"source": source, "type": source_type, "ts": timestamp}
            )
            return True
        except Exception as e:
            logger.error(f"Error adding document {source}: {e}")
            return False

    def add_mention(self, doc_source: str, entity_name: str) -> bool:
        """Create MENTIONS relationship between document and entity."""
        try:
            self._conn.execute(
                """
                MATCH (d:Document {source: $doc}), (e:Entity {name: $entity})
                MERGE (d)-[:MENTIONS]->(e)
                """,
                {"doc": doc_source, "entity": entity_name}
            )
            return True
        except Exception as e:
            logger.error(f"Error adding mention: {e}")
            return False

    def add_relation(
        self,
        from_entity: str,
        to_entity: str,
        relation: str = "RELATED_TO"
    ) -> bool:
        """Create relationship between two entities."""
        try:
            self._conn.execute(
                """
                MATCH (a:Entity {name: $from}), (b:Entity {name: $to})
                MERGE (a)-[:RELATED_TO {relation: $rel}]->(b)
                """,
                {"from": from_entity, "to": to_entity, "rel": relation}
            )
            return True
        except Exception as e:
            logger.error(f"Error adding relation: {e}")
            return False

    # --- Query Operations ---

    def get_related_entities(
        self,
        entity_name: str,
        depth: int = 2,
        limit: int = 20
    ) -> list[dict]:
        """Get entities related to given entity.

        Args:
            entity_name: Starting entity.
            depth: How many hops to traverse.
            limit: Max results.

        Returns:
            List of related entities with path info.
        """
        try:
            result = self._conn.execute(
                f"""
                MATCH (a:Entity {{name: $name}})-[:RELATED_TO*1..{depth}]-(b:Entity)
                WHERE a.name <> b.name
                RETURN DISTINCT b.name AS name, b.type AS type, b.description AS description
                LIMIT $limit
                """,
                {"name": entity_name, "limit": limit}
            )

            entities = []
            while result.has_next():
                row = result.get_next()
                entities.append({
                    "name": row[0],
                    "type": row[1],
                    "description": row[2]
                })

            return entities
        except Exception as e:
            logger.error(f"Error getting related entities: {e}")
            return []

    def find_path(
        self,
        entity1: str,
        entity2: str,
        max_depth: int = 5
    ) -> list[str]:
        """Find shortest path between two entities.

        Returns:
            List of entity names in the path.
        """
        try:
            result = self._conn.execute(
                f"""
                MATCH path = shortestPath(
                    (a:Entity {{name: $e1}})-[:RELATED_TO*1..{max_depth}]-(b:Entity {{name: $e2}})
                )
                RETURN nodes(path)
                """,
                {"e1": entity1, "e2": entity2}
            )

            if result.has_next():
                nodes = result.get_next()[0]
                return [n["name"] for n in nodes]

            return []
        except Exception as e:
            logger.error(f"Error finding path: {e}")
            return []

    def get_documents_for_entity(
        self,
        entity_name: str,
        limit: int = 10
    ) -> list[dict]:
        """Get documents that mention an entity."""
        try:
            result = self._conn.execute(
                """
                MATCH (d:Document)-[:MENTIONS]->(e:Entity {name: $name})
                RETURN d.source AS source, d.source_type AS type
                LIMIT $limit
                """,
                {"name": entity_name, "limit": limit}
            )

            docs = []
            while result.has_next():
                row = result.get_next()
                docs.append({"source": row[0], "type": row[1]})

            return docs
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []

    def get_most_connected(self, limit: int = 10) -> list[dict]:
        """Get most connected entities."""
        try:
            result = self._conn.execute(
                """
                MATCH (e:Entity)-[r]-()
                RETURN e.name AS name, e.type AS type, count(r) AS connections
                ORDER BY connections DESC
                LIMIT $limit
                """,
                {"limit": limit}
            )

            entities = []
            while result.has_next():
                row = result.get_next()
                entities.append({
                    "name": row[0],
                    "type": row[1],
                    "connections": row[2]
                })

            return entities
        except Exception as e:
            logger.error(f"Error getting most connected: {e}")
            return []

    def search_entities(
        self,
        query: str,
        entity_type: str | None = None,
        limit: int = 20
    ) -> list[dict]:
        """Search entities by name pattern."""
        try:
            type_filter = f"AND e.type = '{entity_type}'" if entity_type else ""

            result = self._conn.execute(
                f"""
                MATCH (e:Entity)
                WHERE e.name CONTAINS $query {type_filter}
                RETURN e.name AS name, e.type AS type, e.description AS description
                LIMIT $limit
                """,
                {"query": query, "limit": limit}
            )

            entities = []
            while result.has_next():
                row = result.get_next()
                entities.append({
                    "name": row[0],
                    "type": row[1],
                    "description": row[2]
                })

            return entities
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            return []

    def get_entity_count(self) -> int:
        """Get total entity count."""
        try:
            result = self._conn.execute("MATCH (e:Entity) RETURN count(e)")
            if result.has_next():
                return result.get_next()[0]
            return 0
        except Exception:
            return 0

    def get_relation_count(self) -> int:
        """Get total relation count."""
        try:
            result = self._conn.execute("MATCH ()-[r:RELATED_TO]->() RETURN count(r)")
            if result.has_next():
                return result.get_next()[0]
            return 0
        except Exception:
            return 0

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn = None
        if self._db:
            self._db = None
        logger.info("Kuzu connection closed")


# Global instance
knowledge_graph = KnowledgeGraph()
