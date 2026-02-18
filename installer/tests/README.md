# OpenCode Registry Tests

This directory contains the test suite for the OpenCode Registry CLI tool.

## Running Tests

### Run All Tests

```bash
cd installer
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_version.py
pytest tests/test_manifest.py
pytest tests/test_installed_db.py
pytest tests/test_config.py
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=opencode_config --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

### Run Specific Test

```bash
# By name pattern
pytest -k "test_parse_version"

# By marker
pytest -m "unit"
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── test_config.py           # Configuration management tests
├── test_installed_db.py     # Installation database tests
├── test_manifest.py         # Manifest parsing and validation tests
└── test_version.py          # Semantic versioning tests
```

## Test Coverage

Current coverage for core utilities:

| Module | Coverage | Status |
|--------|----------|--------|
| `utils/version.py` | 89% | ✅ Good |
| `utils/manifest.py` | 94% | ✅ Excellent |
| `utils/installed_db.py` | 100% | ✅ Perfect |
| `config.py` | 86% | ✅ Good |

## Fixtures

Common fixtures available in `conftest.py`:

- `temp_dir` - Temporary directory for test files
- `mock_registry` - Mock OpenCode registry structure
- `mock_agent_md` - Sample agent markdown file
- `mock_skill_md` - Sample skill markdown file
- `mock_command_md` - Sample command markdown file
- `mock_config_dir` - Mock configuration directory
- `mock_target_dir` - Mock installation target directory

## Test Categories

### Unit Tests

Test individual functions and classes in isolation:

- **Version Parsing** - `test_version.py`
  - Semantic version parsing
  - Version comparison
  - Format validation

- **Manifest Parsing** - `test_manifest.py`
  - YAML frontmatter extraction
  - Component manifest creation
  - Validation logic

- **Database Management** - `test_installed_db.py`
  - Component tracking
  - Installation logging
  - Data persistence

- **Configuration** - `test_config.py`
  - Config loading/saving
  - Default values
  - Path detection

## Writing New Tests

### Example Test

```python
def test_my_feature(temp_dir):
    """Test description here."""
    # Arrange
    config = Config(temp_dir / "config.json")
    
    # Act
    config.set("key", "value")
    
    # Assert
    assert config.get("key") == "value"
```

### Best Practices

1. **Use descriptive names**: `test_parse_version_with_v_prefix`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **One assertion per test** (when possible)
4. **Use fixtures** for common setup
5. **Test edge cases** and error conditions
6. **Keep tests independent** - no shared state

## CI/CD Integration

Tests run automatically on:

- Pull requests
- Pushes to main branch
- Pre-commit hooks (optional)

### GitHub Actions (Planned)

```yaml
- name: Run tests
  run: |
    cd installer
    pip install -e ".[dev]"
    pytest tests/ --cov=opencode_config
```

## Troubleshooting

### Test Discovery Issues

If tests aren't being discovered:

```bash
# Check pytest can find tests
pytest --collect-only

# Ensure you're in the installer directory
cd installer
pytest tests/
```

### Import Errors

If you get import errors:

```bash
# Install package in development mode
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

### Fixture Errors

If fixtures aren't working:

```bash
# List available fixtures
pytest --fixtures

# Check conftest.py is in tests/ directory
ls tests/conftest.py
```

## Adding Test Coverage

To add tests for CLI commands (currently 0% coverage):

1. Use Click's `CliRunner` for testing CLI commands
2. Mock filesystem operations
3. Test both success and error paths
4. Verify console output

Example:
```python
from click.testing import CliRunner
from opencode_config.cli import cli

def test_list_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
```

## Questions?

- See [AGENTS.md](../AGENTS.md) for development guide
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
- Open an issue on GitHub for help
