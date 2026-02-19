# Installation Guide

SecureBrainBox can be installed in multiple ways. Choose the one that works best for you.

## Prerequisites

All installation methods require:

- **Docker & Docker Compose** - For running the AI services
- **8GB RAM** - Recommended for running local AI models
- **10GB disk space** - For models and data

## Quick Install Options

### Option 1: curl (Linux/macOS) ⭐ Recommended

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

### Option 5: Windows (via WSL) 🪟

SecureBrainBox runs natively on Windows through **WSL (Windows Subsystem for Linux)**. This gives you a full Linux environment — the same one Docker Desktop uses under the hood.

#### Step 1: Install WSL

Open **PowerShell as Administrator** and run:

```powershell
wsl --install
```

This installs WSL 2 with Ubuntu by default. **Restart your computer** when prompted.

After restart, Ubuntu will open automatically and ask you to create a username and password.

#### Step 2: Install Docker

You have two options:

**Option A: Docker inside WSL (recommended for simplicity)**

```bash
# Inside your WSL terminal
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Log out and back in (close and reopen the terminal)
newgrp docker

# Verify
docker run hello-world
```

**Option B: Docker Desktop with WSL 2 backend**

1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. During install, ensure **"Use WSL 2 instead of Hyper-V"** is checked
3. Open Docker Desktop → Settings → Resources → WSL Integration
4. Enable integration with your Ubuntu distro
5. Verify in WSL terminal: `docker run hello-world`

#### Step 3: Install SecureBrainBox

Inside your WSL terminal:

```bash
curl -sSL https://raw.githubusercontent.com/ericrisco/securebrainbox/main/scripts/install.sh | bash
```

That's it. From here on, everything works exactly like Linux.

#### Tips for Windows users

- **Access WSL files from Windows:** Open File Explorer and go to `\\wsl$\Ubuntu\home\<your-user>`
- **Open WSL terminal:** Type `wsl` in PowerShell, or search for "Ubuntu" in the Start menu
- **GPU passthrough:** WSL 2 supports NVIDIA CUDA automatically if you have the latest GPU drivers installed
- **VS Code:** Install the [WSL extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl) to edit files directly inside WSL

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

**Linux / WSL:**
```bash
sudo systemctl start docker
# Or if systemd is not available in your WSL:
sudo service docker start
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
