# Contributing to SecureBrainBox

Thank you for your interest in contributing! This document provides guidelines for contributing to SecureBrainBox.

## Code of Conduct

Be respectful and inclusive. We're building something cool together.

## How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/ericrisco/securebrainbox/issues)
2. If not, create a new issue with:
   - Clear title describing the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System info (OS, Python version, Docker version)
   - Relevant logs (use `docker compose logs`)

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue with `[Feature]` prefix
3. Describe the feature and use case
4. Explain why it would be valuable

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Run linting: `ruff check .`
6. Commit with conventional commits: `git commit -m 'feat: add feature'`
7. Push: `git push origin feature/my-feature`
8. Open a Pull Request

## Development Setup

```bash
git clone https://github.com/ericrisco/securebrainbox.git
cd securebrainbox
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed setup.

## Code Style

- **Python**: Follow PEP 8, enforced by Ruff
- **Type hints**: Use them for all public functions
- **Docstrings**: Google style
- **Commits**: [Conventional Commits](https://conventionalcommits.org/)

### Commit Types

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Maintenance

## Testing

- Write tests for new features
- Maintain >70% coverage
- Use pytest fixtures
- Mock external services

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src
```

## Documentation

- Update README for user-facing changes
- Update relevant docs in `docs/`
- Add docstrings to new code
- Include examples where helpful

## Review Process

1. All PRs require review
2. CI must pass
3. Keep PRs focused and small
4. Respond to feedback promptly

## Questions?

- Open a [Discussion](https://github.com/ericrisco/securebrainbox/discussions)
- Check existing issues
- Read the documentation

Thank you for contributing! 🧠
