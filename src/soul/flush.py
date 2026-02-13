"""Pre-compaction memory flush for saving important context."""

import logging

logger = logging.getLogger(__name__)


FLUSH_PROMPT = """The conversation context is about to be compacted (summarized to save space).

Review the recent conversation and identify anything that should be saved to memory.

**Save to daily log** (temporary, day-to-day notes):
- Tasks completed or started
- Decisions made during conversation
- Important facts mentioned
- Questions that were answered

**Save to long-term memory** (permanent, lasting information):
- User preferences discovered
- Project milestones or key decisions
- Important learnings or insights
- Information the user explicitly asked to remember

Based on the conversation below, respond with what should be saved:

---
RECENT CONVERSATION:
{conversation}
---

Respond in this format:

DAILY_LOG:
- [item to save to daily log]
- [another item]

LONG_TERM:
- [item to save to long-term memory]
- [another item]

If nothing needs to be saved, respond with:
NOTHING_TO_SAVE

Be selective - only save genuinely important information."""


class MemoryFlusher:
    """Handle pre-compaction memory flush.

    Before context is compacted, this extracts important information
    and saves it to appropriate memory files.
    """

    def __init__(self, memory_manager, llm_client):
        """Initialize flusher.

        Args:
            memory_manager: MemoryManager instance.
            llm_client: LLM client for extraction.
        """
        self.memory = memory_manager
        self.llm = llm_client

    async def flush(self, conversation_context: str) -> dict:
        """Trigger memory flush before compaction.

        Args:
            conversation_context: Recent conversation text.

        Returns:
            Dict with saved items count.
        """
        if not conversation_context or len(conversation_context) < 100:
            logger.debug("Conversation too short for flush")
            return {"daily_log": 0, "long_term": 0, "skipped": True}

        try:
            # Generate flush prompt
            prompt = FLUSH_PROMPT.format(
                conversation=conversation_context[:8000]  # Limit size
            )

            response = await self.llm.generate(prompt, max_tokens=500)

            # Parse response
            result = self._parse_flush_response(response)

            # Save to memory
            saved = {"daily_log": 0, "long_term": 0, "skipped": False}

            for item in result.get("daily_log", []):
                await self.memory.append_log(item, section="Memory Flush")
                saved["daily_log"] += 1

            for item in result.get("long_term", []):
                await self.memory.append_to_memory("Learnings", item)
                saved["long_term"] += 1

            logger.info(
                f"Memory flush complete: "
                f"{saved['daily_log']} daily, {saved['long_term']} long-term"
            )

            return saved

        except Exception as e:
            logger.error(f"Memory flush failed: {e}")
            return {"daily_log": 0, "long_term": 0, "error": str(e)}

    def _parse_flush_response(self, response: str) -> dict:
        """Parse LLM response into items to save.

        Args:
            response: LLM response text.

        Returns:
            Dict with daily_log and long_term lists.
        """
        result = {"daily_log": [], "long_term": []}

        if "NOTHING_TO_SAVE" in response:
            return result

        current_section = None

        for line in response.split("\n"):
            line = line.strip()

            if "DAILY_LOG:" in line:
                current_section = "daily_log"
            elif "LONG_TERM:" in line:
                current_section = "long_term"
            elif line.startswith("-") and current_section:
                item = line[1:].strip()
                if item:
                    result[current_section].append(item)

        return result

    async def quick_save(self, content: str, to_long_term: bool = False) -> bool:
        """Quickly save content without LLM analysis.

        Args:
            content: Content to save.
            to_long_term: If True, save to MEMORY.md; else to daily log.

        Returns:
            True if saved successfully.
        """
        try:
            if to_long_term:
                await self.memory.append_to_memory("Notes", content)
            else:
                await self.memory.append_log(content, section="Quick Save")
            return True
        except Exception as e:
            logger.error(f"Quick save failed: {e}")
            return False


# Helper function for manual memory saves
async def save_to_memory(content: str, long_term: bool = False) -> bool:
    """Save content to memory.

    Args:
        content: Content to save.
        long_term: If True, save to MEMORY.md.

    Returns:
        True if successful.
    """
    from src.soul.memory import get_memory_manager
    from src.utils.llm import llm_client

    manager = get_memory_manager()
    flusher = MemoryFlusher(manager, llm_client)

    return await flusher.quick_save(content, to_long_term=long_term)
