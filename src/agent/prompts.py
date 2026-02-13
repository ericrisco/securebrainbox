"""System prompts and templates for the agent."""

# Main system prompt that defines the agent's personality
SYSTEM_PROMPT = """You are SecureBrain, a personal knowledge assistant.

Your job is to:
1. Answer questions based on the user's personal knowledge base
2. Be precise and cite sources when possible
3. Admit when you don't have enough information
4. Connect ideas from different sources when relevant
5. Be helpful, concise, and friendly

Important guidelines:
- Always respond in the same language the user uses
- If the context doesn't contain relevant information, say so clearly
- When citing sources, mention them naturally in your response
- Keep responses focused and avoid unnecessary verbosity
- If asked about something not in the knowledge base, offer to help index relevant content

You are running 100% locally - all data stays on the user's machine."""

# Template for RAG (Retrieval-Augmented Generation) queries
RAG_PROMPT_TEMPLATE = """Based on the following context from the user's knowledge base, answer the question.

CONTEXT:
{context}

QUESTION:
{query}

INSTRUCTIONS:
- Use ONLY the information from the provided context
- If the context doesn't contain relevant information, clearly state that
- Cite sources naturally when using specific information (e.g., "According to [source]...")
- Be concise and direct
- If multiple sources provide information, synthesize them coherently

RESPONSE:"""

# Template for when no context is found
NO_CONTEXT_PROMPT = """The user asked a question but no relevant information was found in their knowledge base.

QUESTION: {query}

Please:
1. Acknowledge that you couldn't find relevant information in their knowledge base
2. Offer a general response if you can help
3. Suggest they could index relevant content by sending documents, URLs, or text

Keep your response helpful and friendly."""

# Confirmation message after indexing content
INDEXING_CONFIRMATION = """✅ *Content indexed successfully!*

📄 *Source:* `{source}`
📊 *Type:* {source_type}
🧩 *Chunks:* {chunk_count}

You can now ask me questions about this content."""

# Status message template
STATUS_MESSAGE = """🔧 *System Status*

*Services:*
{ollama_status} Ollama (LLM)
{weaviate_status} Weaviate (Vector DB)

*Models:*
🤖 LLM: `{llm_model}`
📊 Embeddings: `{embed_model}`

*Knowledge Base:*
📚 Total chunks: {total_chunks}
"""

# Error messages
ERROR_MESSAGES = {
    "connection_failed": (
        "❌ *Connection Error*\n\n"
        "Could not connect to AI services. "
        "Please check if Docker containers are running:\n"
        "`sbb status`"
    ),
    "generation_failed": (
        "❌ *Generation Error*\n\n"
        "Failed to generate a response. "
        "The AI model might be busy or unavailable. "
        "Please try again."
    ),
    "indexing_failed": (
        "❌ *Indexing Error*\n\n"
        "Failed to index the content. "
        "Please check the logs for details."
    ),
}

# Help text for commands
HELP_TEXT = """📚 *SecureBrainBox Commands*

*Basic Commands:*
/start - Welcome message
/help - Show this help
/status - Check system health

*Knowledge Base:*
/search <query> - Search your knowledge
/stats - Show knowledge base statistics

*Knowledge Graph:*
/graph <entity> - Explore entity connections
/ideas <topic> - Generate creative ideas

*Indexing Content:*
Send me any of these to index:
• 📄 Documents (PDF, DOCX, TXT)
• 🖼️ Images (with AI description)
• 🎤 Voice messages (transcribed)
• 🔗 URLs (content extracted)
• 💬 Text messages

*Tips:*
• Just send content to index it automatically
• Ask questions naturally to search your knowledge
• Use /graph to explore connections between concepts
• Use /ideas to get creative suggestions from your knowledge
"""

# Ideas generation prompt
IDEAS_PROMPT = """Based on the user's knowledge base, generate creative ideas related to the given topic.

TOPIC: {topic}

RELEVANT CONTEXT FROM KNOWLEDGE BASE:
{context}

Generate 3-5 creative ideas that:
1. Connect different concepts from the knowledge base
2. Are practical and actionable
3. Might not be immediately obvious

Format each idea as:
💡 **Idea Title**
Brief description of the idea and why it's interesting.

Be creative but grounded in the available information."""
