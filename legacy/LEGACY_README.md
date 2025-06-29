# Legacy Files

This folder contains the original files from the previous system before reorganization into the composable framework.

## Original Python Files

- **`tool_call_latency_demo.py`** - Original latency measurement script
- **`tool_call_accuracy_test.py`** - Original accuracy testing framework  
- **`trading_terminal_test.py`** - Original trading-specific test script
- **`analyze_trading_results.py`** - Original analysis script for trading results
- **`custom_test_example.py`** - Example of how to use the old system

## Original Documentation

- **`README.md`** - Original project README
- **`TOOL_ACCURACY_README.md`** - Documentation for the old accuracy testing
- **`TRADING_TERMINAL_README.md`** - Documentation for the old trading tests

## Migration Notes

These files have been replaced by the new composable system:

### Old → New Mapping
- `tool_call_latency_demo.py` → Any test with `main.py` (all tests measure latency)
- `tool_call_accuracy_test.py` → `test_suites/base_test_suite.py` + `config/test_scenarios.json`
- `trading_terminal_test.py` → `test_suites/base_test_suite.py` + `config/trading_scenarios.json`
- `analyze_trading_results.py` → `analyzers/combined_analyzer.py`
- `custom_test_example.py` → `example_usage.py`

### Key Improvements in New System
- **Composable**: Mix any reasoning strategy with any test configuration
- **Unified**: Single measurement captures accuracy, latency, and token usage
- **Configurable**: Scenarios defined in JSON files, not hardcoded
- **Extensible**: Easy to add new strategies and scenario types
- **Clean**: No code duplication between different test types

## Usage
These files are kept for reference but should not be used in new development. Use the new system via `main.py` instead. 