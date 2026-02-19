"""Tests for bot module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestBotCommands:
    """Test bot command handlers."""

    @pytest.fixture
    def mock_update(self):
        """Create a mock Telegram Update object."""
        update = MagicMock()
        update.effective_user.id = 12345
        update.effective_user.username = "testuser"
        update.effective_chat.id = 12345
        update.effective_chat.type = "private"
        update.message.text = "/start"
        update.message.reply_text = AsyncMock()
        update.message.chat.send_action = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create a mock Telegram Context object."""
        context = MagicMock()
        context.args = []
        return context

    @pytest.mark.asyncio
    async def test_start_command(self, mock_update, mock_context):
        """Test /start command sends welcome message."""
        from src.bot.commands import start_command

        await start_command(mock_update, mock_context)

        # May be called multiple times (bootstrap flow)
        mock_update.message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_help_command(self, mock_update, mock_context):
        """Test /help command shows available commands."""
        from src.bot.commands import help_command

        mock_update.message.text = "/help"

        await help_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        message = call_args[0][0]

        assert "/start" in message
        assert "/help" in message
        assert "/status" in message

    @pytest.mark.asyncio
    async def test_search_command_without_query(self, mock_update, mock_context):
        """Test /search command without query shows usage."""
        from src.bot.commands import search_command

        mock_update.message.text = "/search"
        mock_context.args = []

        await search_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        message = call_args[0][0]

        assert "Usage" in message or "usage" in message.lower()

    @pytest.mark.asyncio
    async def test_search_command_with_query(self, mock_update, mock_context):
        """Test /search command with query."""

        mock_update.message.text = "/search test query"
        mock_context.args = ["test", "query"]

        # Mock the agent to avoid real connections
        mock_agent = MagicMock()
        mock_agent.search = AsyncMock(return_value=[])

        with patch.dict("sys.modules", {}):
            pass

        with patch("src.agent.brain.agent", mock_agent):
            from src.bot.commands import search_command

            await search_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called()
        # Check that at least one call mentions the query
        all_calls = mock_update.message.reply_text.call_args_list
        messages = " ".join(str(c) for c in all_calls)
        assert "test query" in messages


class TestBotHandlers:
    """Test bot message handlers."""

    @pytest.fixture
    def mock_update(self):
        """Create a mock Telegram Update object."""
        update = MagicMock()
        update.effective_user.id = 12345
        update.effective_user.username = "testuser"
        update.effective_chat.id = 12345
        update.message.text = "Hello, bot!"
        update.message.reply_text = AsyncMock()
        update.message.chat.send_action = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create a mock Telegram Context object."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_handle_text_message(self, mock_update, mock_context):
        """Test text message handler processes message."""
        from src.bot.handlers import handle_text_message

        # Mock onboarding as complete so we go through normal flow
        mock_onboarding = MagicMock()
        mock_onboarding.is_complete.return_value = True

        mock_agent = MagicMock()
        mock_agent.process_query = AsyncMock(return_value="Hello!")

        with (
            patch("src.soul.bootstrap.get_onboarding", return_value=mock_onboarding),
            patch("src.bot.handlers.agent", mock_agent),
        ):
            await handle_text_message(mock_update, mock_context)

        # Should send typing action
        mock_update.message.chat.send_action.assert_called()

        # Should reply with something
        mock_update.message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_handle_document(self, mock_update, mock_context):
        """Test document handler acknowledges document."""
        from src.bot.handlers import handle_document

        # Setup document mock
        mock_update.message.document = MagicMock()
        mock_update.message.document.file_name = "test.pdf"
        mock_update.message.document.file_size = 1024
        mock_update.message.document.mime_type = "application/pdf"
        mock_update.message.document.get_file = AsyncMock()

        await handle_document(mock_update, mock_context)

        mock_update.message.reply_text.assert_called()
        all_calls = mock_update.message.reply_text.call_args_list
        messages = " ".join(str(c) for c in all_calls)
        assert "test.pdf" in messages

    @pytest.mark.asyncio
    async def test_handle_photo(self, mock_update, mock_context):
        """Test photo handler acknowledges photo."""
        from src.bot.handlers import handle_photo

        # Setup photo mock
        mock_photo = MagicMock()
        mock_photo.width = 800
        mock_photo.height = 600
        mock_photo.get_file = AsyncMock()
        mock_update.message.photo = [mock_photo]
        mock_update.message.caption = None

        await handle_photo(mock_update, mock_context)

        mock_update.message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_handle_voice(self, mock_update, mock_context):
        """Test voice handler acknowledges voice message."""
        from src.bot.handlers import handle_voice

        # Setup voice mock
        mock_update.message.voice = MagicMock()
        mock_update.message.voice.duration = 30
        mock_update.message.voice.get_file = AsyncMock()
        mock_update.message.audio = None

        await handle_voice(mock_update, mock_context)

        mock_update.message.reply_text.assert_called()


class TestBotApp:
    """Test bot application creation."""

    def test_create_application_without_token(self):
        """Test that application creation fails without token."""
        from src.bot.app import create_application

        with patch("src.bot.app.settings") as mock_settings:
            mock_settings.telegram_bot_token = ""

            with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
                create_application()

    def test_create_application_with_token(self):
        """Test that application is created with valid token."""
        from src.bot.app import create_application

        with patch("src.bot.app.settings") as mock_settings:
            mock_settings.telegram_bot_token = "fake:token"

            # Should not raise
            app = create_application()
            assert app is not None
