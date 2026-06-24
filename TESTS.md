# Testing Universal Notifier

## Quick Start

**Prerequisites:** [uv](https://docs.astral.sh/uv/) installed, Python 3.13+

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov --cov-report=html
# Then open htmlcov/index.html in your browser
```

**VS Code users:** Press `Ctrl+Shift+P` → "Tasks: Run Task" → select one of:
- `Test: Run All` — verbose test execution
- `Test: Coverage` — coverage with missing lines
- `Test: HTML Report` — generate browsable HTML report

---

## Test Structure

### File Map

| Test File | Module Under Test | What It Tests |
|-----------|-------------------|---------------|
| `tests/test_init.py` | `__init__.py` | Service registration, channel routing, DND logic, greetings, title/prefix, Telegram routing, notification modes |
| `tests/test_config_flow.py` | `config_flow.py` | Config flow helpers (greetings text↔dict, time slots↔fields), flow handler steps |
| `tests/test_utils.py` | `utils.py` | Pure functions: TTS duration, time ranges, slot info, callers, text formatting |
| `tests/test_sensor.py` | `sensor.py` | Volume sensor (state + attributes), family sensor (presence), default player sensor |
| `tests/test_binary_sensor.py` | `binary_sensor.py` | DND sensor (time slots, weekday/weekend, override switch interaction) |
| `tests/test_select.py` | `select.py` | Priority volume, text format, notification mode select entities |
| `tests/test_switch.py` | `switch.py` | DND override switch (on/off toggle, default state) |
| `tests/test_text.py` | `text.py` | Last message text entity (state, attributes, value set) |
| `tests/test_number.py` | `number.py` | Voice buffer number entity (state, attributes, value set) |

### conftest.py — Shared Fixtures

The `tests/conftest.py` file provides all shared test infrastructure:

**Constants:**
- `DEFAULT_DATA` — complete configuration dict matching config flow defaults (time slots, DND, greetings, channels)

**Mock Classes:**
- `MockServiceRegistry` — simulates `hass.services` with handler registration and call recording
- `MockStatesManager` — simulates `hass.states` with get/set support

**Fixtures:**
- `_patch_dt_util_now` (autouse) — patches HA's `dt_util.now()` so `@freeze_time` works correctly
- `hass` — MagicMock-based hass with real service registry and states manager
- `mock_config_entry` — MagicMock config entry with standard configuration
- `setup_integration` — calls `async_setup_entry` to register services and initialize runtime data
- `service_calls` — access to recorded service calls during a test
- `_call_send` — helper to call `universal_notifier.send` with automatic voice queue draining
- `voice_calls` — filtered service calls for voice-related domains only

---

## Running Tests

### Local (Primary)

```bash
# All tests, quiet mode
uv run pytest

# All tests, verbose
uv run pytest -v

# Single file
uv run pytest tests/test_utils.py -v

# Single class
uv run pytest tests/test_init.py::TestDNDLogic -v

# Single test
uv run pytest tests/test_utils.py::TestIsTimeInRange::test_overnight_range_inside -v

# By keyword
uv run pytest -k "dnd" -v

# Stop on first failure
uv run pytest -x

# Show print output
uv run pytest -s
```

### Docker (Optional)

```bash
# Run all tests in isolated container
docker compose run test-runner

# With verbose output
docker compose run test-runner uv run pytest -v
```

### VS Code Tasks

`Ctrl+Shift+P` → "Tasks: Run Task" → select:
- **Test: Run All** — `uv run pytest tests/ -v`
- **Test: Coverage** — `uv run pytest tests/ --cov --cov-report=term-missing`
- **Test: HTML Report** — `uv run pytest tests/ --cov --cov-report=html`

---

## Coverage

### Terminal Report

```bash
uv run pytest --cov --cov-report=term-missing
```

Output shows each file with line numbers of uncovered code:

```
Name                                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------------
custom_components/universal_notifier/utils.py     85      3    96%   142, 156, 178
```

### HTML Report

```bash
uv run pytest --cov --cov-report=html
```

Opens an interactive report in `htmlcov/index.html`. Click any file to see line-by-line coverage highlighting.

### Configuration

Coverage settings in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["custom_components"]

[tool.coverage.report]
show_missing = true
```

---

## Writing New Tests

### Conventions

- **File naming:** `test_<module>.py` matching the source module
- **Class naming:** `class Test<Feature>:` grouping related tests
- **Method naming:** `def test_<behavior>:` describing what is verified
- **Docstrings:** every test has a docstring explaining what it checks
- **Imports:** import from `custom_components.universal_notifier.<module>` and `tests.conftest`

### Patterns

**Entity test (no integration setup):**
```python
from unittest.mock import MagicMock
from custom_components.universal_notifier.sensor import UNotifierVolumeSensor

def test_volume_sensor_state():
    """Volume sensor should report current slot volume as percentage."""
    conf = DEFAULT_DATA.copy()
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    sensor = UNotifierVolumeSensor(conf, entry)
    assert sensor.native_value is not None
```

**Integration test (with full setup):**
```python
from freezegun import freeze_time

class TestMyFeature:
    @freeze_time("2026-06-17 10:00:00")
    async def test_my_behavior(self, hass, _call_send, service_calls):
        """Description of what this test verifies."""
        await _call_send(
            message="Test",
            targets=["test_text"],
        )
        assert len(service_calls) >= 1
```

**Time-dependent test:**
```python
from freezegun import freeze_time

class TestTimeFeature:
    @freeze_time("2026-06-17 02:00:00")  # Wednesday 02:00
    def test_during_dnd(self):
        # ... test logic
        pass
```

### Step-by-Step: Adding a Test

1. Identify which `test_<module>.py` file matches your change
2. Find or create a `class Test<Feature>:` that groups related tests
3. Write the test method with a descriptive name and docstring
4. Use `@freeze_time(...)` if the behavior depends on time
5. Use `_call_send` fixture for service-level integration tests
6. Use direct entity instantiation for entity-level unit tests
7. Run: `uv run pytest tests/test_<module>.py::TestFeature::test_name -v`
8. Verify it passes, then commit

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'custom_components'"

Run `uv sync` to install the project in development mode.

### freezegun not affecting HA's dt_util.now()

The autouse `_patch_dt_util_now` fixture in `conftest.py` handles this automatically. If you're writing a test outside the `tests/` directory or mocking `dt_util` yourself, ensure you patch `homeassistant.util.dt.now`.

### "takes N positional arguments but M were given"

Check the constructor signature of the entity you're testing. Entity constructors vary:
- Most entities: `__init__(self, conf, entry)`
- Entities needing hass: `__init__(self, hass, conf, entry)` or `__init__(self, hass, entry)`

Read the source file to confirm before writing tests.

### asyncio warnings or "coroutine was never awaited"

Ensure `asyncio_mode = "auto"` is set in `pyproject.toml` (already configured). Async test methods are automatically detected.

### Tests pass locally but fail in Docker

The Dockerfile.test uses Python 3.14. Ensure your local Python version matches or check for version-specific behavior in the error output.
