# Installation Guide

SecureBrainBox can be installed in multiple ways. Choose the one that works best for you.

## Prerequisites

All installation methods require:

- **Docker & Docker Compose** - For running the AI services
- **8GB RAM** - Recommended for running local AI models
- **10GB disk space** - For models and data

## Quick Install Options

### Option 1: curl (Mac/Linux) ⭐ Recommended

```bash
curl -sSL https://get.securebrainbox.dev | bash
```

Or using the GitHub raw URL:

```bash
curl -sSL https://raw.githubusercontent.com/ericrisco/securebrainbox/main/scripts/install.sh | bash
```

### Option 2: Homebrew (Mac)

```bash
brew tap ericrisco/tap
brew install securebrainbox
```

Or in one command:

```bash
brew install ericrisco/tap/securebrainbox
```

### Option 3: npm/npx (Node.js users)

```bash
# Run directly without installing
npx securebrainbox install

# Or install globally
npm install -g securebrainbox
sbb install
```

### Option 4: pip (Python users)

```bash
pip install securebrainbox
sbb install
```

## After Installation

Run the setup wizard:

```bash
sbb install
```

This will guide you through:

1. ✅ **Docker check** - Verifies Docker is installed and running
2. 🤖 **Telegram bot setup** - Helps you create a bot with @BotFather
3. ⚙️ **Configuration** - Creates your `.env` file
4. 🚀 **Start services** - Launches Docker containers
5. 📦 **Download models** - Gets AI models (~4GB)

## Manual Installation (Developers)

If you prefer to set things up manually:

```bash
# Clone the repository
git clone https://github.com/ericrisco/securebrainbox.git
cd securebrainbox

# Copy environment template
cp .env.example .env

# Edit .env and add your Telegram bot token
# Get one from @BotFather on Telegram
nano .env

# Start services
docker-compose up -d

# Download AI models
docker-compose exec ollama ollama pull gemma3
docker-compose exec ollama ollama pull nomic-embed-text

# Check logs
docker-compose logs -f app
```

## CLI Commands

After installation, these commands are available:

| Command | Description |
|---------|-------------|
| `sbb install` | Run setup wizard |
| `sbb start` | Start all services |
| `sbb stop` | Stop all services |
| `sbb restart` | Restart services |
| `sbb status` | Show service status |
| `sbb logs` | View recent logs |
| `sbb logs -f` | Follow live logs |
| `sbb config show` | Show configuration |
| `sbb config set KEY VALUE` | Update config |
| `sbb config token TOKEN` | Set Telegram token |

## Troubleshooting

### Docker not found

Install Docker from: https://docs.docker.com/get-docker/

**Mac:**
```bash
brew install --cask docker
```

**Linux:**
```bash
curl -fsSL https://get.docker.com | sh
```

### Docker not running

**Mac:** Open Docker Desktop from Applications

**Linux:**
```bash
sudo systemctl start docker
```

### Command not found: sbb

Add `~/.local/bin` to your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# Reload
source ~/.bashrc  # or source ~/.zshrc
```

### Models download timeout

Download models manually:

```bash
docker-compose exec ollama ollama pull gemma3
docker-compose exec ollama ollama pull nomic-embed-text
```

### Out of memory

Try using smaller models:

```bash
sbb config set OLLAMA_MODEL gemma3:2b
sbb restart
```

## Uninstall

```bash
# Stop services
sbb stop

# Remove Docker volumes
cd ~/.securebrainbox/app
docker-compose down -v

# Remove installation
rm -rf ~/.securebrainbox
rm ~/.local/bin/sbb
rm ~/.local/bin/securebrainbox

# Homebrew users
brew uninstall securebrainbox

# npm users
npm uninstall -g securebrainbox

# pip users
pip uninstall securebrainbox
```

## Getting Help

- **GitHub Issues:** https://github.com/ericrisco/securebrainbox/issues
- **Documentation:** https://github.com/ericrisco/securebrainbox#readme
