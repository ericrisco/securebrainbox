#!/bin/bash
# SecureBrainBox Installer
# Usage: curl -sSL https://get.securebrainbox.dev | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
DIM='\033[2m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
cat << 'EOF'
  ____                           ____            _       ____            
 / ___|  ___  ___ _   _ _ __ ___| __ ) _ __ __ _(_)_ __ | __ )  _____  __
 \___ \ / _ \/ __| | | | '__/ _ \  _ \| '__/ _` | | '_ \|  _ \ / _ \ \/ /
  ___) |  __/ (__| |_| | | |  __/ |_) | | | (_| | | | | | |_) | (_) >  < 
 |____/ \___|\___|\__,_|_|  \___|____/|_|  \__,_|_|_| |_|____/ \___/_/\_\
EOF
echo -e "${NC}"
echo "Your private second brain that never forgets."
echo -e "${DIM}100% local • No cloud • Full privacy${NC}"
echo ""

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"

echo -e "${DIM}Detected: $OS ($ARCH)${NC}"
echo ""

# ============================================
# Step 1: Check Docker
# ============================================
echo -e "${BLUE}[1/4]${NC} Checking Docker..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found!${NC}"
    echo ""
    echo "Please install Docker first:"
    if [[ "$OS" == "Darwin" ]]; then
        echo "  brew install --cask docker"
        echo "  # or download from: https://docs.docker.com/desktop/mac/install/"
    else
        echo "  curl -fsSL https://get.docker.com | sh"
        echo "  # or visit: https://docs.docker.com/get-docker/"
    fi
    exit 1
fi

echo -e "${GREEN}✅ Docker found${NC}"

# Check Docker running
if ! docker info &> /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo ""
    if [[ "$OS" == "Darwin" ]]; then
        echo "Please start Docker Desktop and try again."
    else
        echo "Please start Docker: sudo systemctl start docker"
    fi
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Check Docker Compose
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}❌ Docker Compose not found!${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose available${NC}"
echo ""

# ============================================
# Step 2: Install SecureBrainBox
# ============================================
echo -e "${BLUE}[2/4]${NC} Installing SecureBrainBox..."

INSTALL_DIR="${HOME}/.securebrainbox"
APP_DIR="${INSTALL_DIR}/app"
BIN_DIR="${HOME}/.local/bin"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Clone or update repo
if [ -d "$APP_DIR/.git" ]; then
    echo -e "${DIM}Updating existing installation...${NC}"
    cd "$APP_DIR"
    git pull --quiet origin main
else
    echo -e "${DIM}Downloading SecureBrainBox...${NC}"
    if command -v git &> /dev/null; then
        git clone --depth 1 --quiet https://github.com/ericrisco/securebrainbox.git "$APP_DIR"
    else
        # Fallback: download tarball
        mkdir -p "$APP_DIR"
        curl -sL https://github.com/ericrisco/securebrainbox/archive/main.tar.gz | tar xz -C "$APP_DIR" --strip-components=1
    fi
fi

echo -e "${GREEN}✅ SecureBrainBox downloaded${NC}"
echo ""

# ============================================
# Step 3: Setup Python environment
# ============================================
echo -e "${BLUE}[3/4]${NC} Setting up Python environment..."

cd "$APP_DIR"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found!${NC}"
    echo ""
    if [[ "$OS" == "Darwin" ]]; then
        echo "Install with: brew install python@3.11"
    else
        echo "Install with: sudo apt install python3 python3-venv"
    fi
    exit 1
fi

# Create venv if needed
if [ ! -d ".venv" ]; then
    echo -e "${DIM}Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

# Install package
echo -e "${DIM}Installing dependencies...${NC}"
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet .
deactivate

echo -e "${GREEN}✅ Python environment ready${NC}"
echo ""

# ============================================
# Step 4: Create CLI wrapper
# ============================================
echo -e "${BLUE}[4/4]${NC} Creating CLI command..."

# Create wrapper script
cat > "$BIN_DIR/sbb" << 'WRAPPER'
#!/bin/bash
# SecureBrainBox CLI wrapper

INSTALL_DIR="${HOME}/.securebrainbox/app"

if [ ! -d "$INSTALL_DIR" ]; then
    echo "SecureBrainBox not installed. Run the installer:"
    echo "  curl -sSL https://get.securebrainbox.dev | bash"
    exit 1
fi

cd "$INSTALL_DIR"
source .venv/bin/activate
python -m src.cli.main "$@"
WRAPPER

chmod +x "$BIN_DIR/sbb"

# Also create long alias
ln -sf "$BIN_DIR/sbb" "$BIN_DIR/securebrainbox" 2>/dev/null || true

echo -e "${GREEN}✅ CLI ready${NC}"
echo ""

# ============================================
# Check PATH
# ============================================
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "${YELLOW}⚠️  Add this to your shell profile (~/.bashrc, ~/.zshrc):${NC}"
    echo ""
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo -e "${DIM}Then restart your terminal or run: source ~/.bashrc${NC}"
    echo ""
fi

# ============================================
# Done!
# ============================================
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ SecureBrainBox installed successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next step - run the setup wizard:"
echo ""
echo -e "    ${BLUE}sbb install${NC}"
echo ""
echo "This will configure your Telegram bot and start services."
echo ""
