"""Tests for CLI commands."""

from src.cli.main import cli


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help(self, runner):
        """Test CLI shows help."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "SecureBrainBox" in result.output
        assert "install" in result.output
        assert "start" in result.output

    def test_cli_version(self, runner):
        """Test CLI shows version."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "SecureBrainBox" in result.output


class TestInstallCommand:
    """Test install wizard."""

    def test_install_help(self, runner):
        """Test install command help."""
        result = runner.invoke(cli, ["install", "--help"])
        assert result.exit_code == 0
        assert "Install and configure" in result.output

    def test_install_no_docker(self, runner, mocker):
        """Test install fails without Docker."""
        mocker.patch("src.cli.install.check_docker", return_value=False)

        result = runner.invoke(cli, ["install", "--non-interactive", "--token", "fake-token"])

        assert result.exit_code != 0
        assert "Docker" in result.output

    def test_install_no_token_non_interactive(self, runner, mocker):
        """Test install requires token in non-interactive mode."""
        mocker.patch("src.cli.install.check_docker", return_value=True)
        mocker.patch("src.cli.install.check_docker_compose", return_value=True)

        result = runner.invoke(cli, ["install", "--non-interactive"])

        assert result.exit_code != 0
        assert "token" in result.output.lower()


class TestConfigCommands:
    """Test config commands."""

    def test_config_show(self, runner):
        """Test config show command."""
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0
        assert "Configuration" in result.output

    def test_config_set_unknown_key_aborts(self, runner, temp_env):
        """Test config set with unknown key asks for confirmation."""
        result = runner.invoke(cli, ["config", "set", "UNKNOWN_KEY", "value"], input="n\n")
        assert result.exit_code == 0
        assert "Unknown key" in result.output

    def test_config_token_too_short(self, runner, temp_env):
        """Test config token rejects short tokens."""
        result = runner.invoke(cli, ["config", "token", "short"])
        assert "invalid" in result.output.lower()


class TestServiceCommands:
    """Test service control commands."""

    def test_start_command(self, runner, mock_docker):
        """Test start command runs docker compose."""
        result = runner.invoke(cli, ["start"])
        assert result.exit_code == 0
        assert "started" in result.output.lower()

    def test_stop_command(self, runner, mock_docker):
        """Test stop command runs docker compose."""
        result = runner.invoke(cli, ["stop"])
        assert result.exit_code == 0
        assert "stopped" in result.output.lower()

    def test_status_command(self, runner, mock_docker):
        """Test status command."""
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0

    def test_logs_help(self, runner):
        """Test logs command help."""
        result = runner.invoke(cli, ["logs", "--help"])
        assert result.exit_code == 0
        assert "--follow" in result.output
