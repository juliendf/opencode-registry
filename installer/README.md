# OpenCode Registry Installer

Python CLI tool for managing OpenCode components.

## Installation

### For Regular Users

```bash
cd installer
pip install -e .
```

### For Developers

```bash
cd installer
pip install -e ".[dev]"
```

**What's included in `[dev]`?**
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatter
- `ruff` - Fast Python linter
- `mypy` - Type checking

**Note:** Both commands must be run from the `installer/` directory. The `-e` flag installs in "editable" mode, so changes to the source code are immediately reflected.

### From PyPI (Future)

```bash
pip install opencode-config
```

## Usage

See main [README](../README.md) for usage instructions.

## Development

### Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint
ruff check src/
```

### Project Structure

```
installer/
├── src/
│   └── opencode_config/
│       ├── cli.py              # Main CLI entry point
│       ├── config.py           # Configuration management
│       ├── commands/           # CLI commands
│       │   ├── install.py
│       │   ├── list_cmd.py
│       │   ├── status.py
│       │   ├── info.py
│       │   └── ...
│       └── utils/              # Utilities
│           ├── installed_db.py # installed.json management
│           ├── manifest.py     # Manifest parsing
│           └── stow.py         # Stow integration
└── tests/                      # Tests
```

## License

MIT
