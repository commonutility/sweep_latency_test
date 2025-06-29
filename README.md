# Composable Model Performance Testing Framework

A reorganized, modular framework for testing model performance on tool calling tasks. The system separates **reasoning strategies**, **test suites**, and **analysis** into composable components.

## Architecture Overview

```
main.py (orchestrator)
├── reasoning_strategies/    # How models process scenarios
│   ├── openai_strategy.py   # OpenAI API integration
│   └── custom_strategy.py   # Rule-based/custom logic
├── test_suites/            # Configurable test scenarios
│   ├── base_test_suite.py   # Loads scenarios from config files
│   └── validation.py        # Test validation logic
├── analyzers/              # How to analyze results
│   └── combined_analyzer.py    # Accuracy + latency analysis
├── tool_params/            # Tool definitions and data structures
│   └── tool_definitions.py     # Common data structures & tools
├── config/                 # Test scenario definitions
│   ├── test_scenarios.json     # General scenarios
│   └── trading_scenarios.json  # Trading-specific scenarios
├── results/                # Test result outputs
└── legacy/                 # Original system files (deprecated)
```

## Key Concepts

### 🧠 Reasoning Strategies
**How** a model/system processes test scenarios:
- **OpenAI Strategy**: Uses OpenAI API for tool calling
- **Custom Strategy**: Rule-based logic with keyword matching
- **Extensible**: Easy to add new strategies (Claude, local models, etc.)

### 📋 Test Configuration  
**What** scenarios to test (configured via JSON files):
- **General Scenarios**: Weather, math, search, email scenarios
- **Trading Scenarios**: Trading terminal UI interactions (price charts, orders, options)
- **Flexible**: Load any scenario type from configuration files

### 📊 Analysis
**How** to analyze results:
- **Every test automatically measures**: accuracy, latency, and token usage
- **Combined analysis**: Comprehensive insights across all metrics
- **Domain agnostic**: Same analysis works for all scenario types

## Quick Start

### Command Line Usage

```bash
# Test OpenAI o3 model with default scenarios
python main.py --strategy openai --model o3

# Test with custom strategy using trading scenarios  
python main.py --strategy custom --config config/trading_scenarios.json

# Filter by tags and save to specific directory
python main.py --strategy openai --tags weather math --output-dir my_results

# Use specific config file and quiet mode
python main.py --strategy openai --config config/test_scenarios.json --quiet
```

### Programmatic Usage

```python
from main import create_reasoning_strategy, create_test_suite, ModelPerformanceTester
from analyzers.combined_analyzer import CombinedAnalyzer

# Create components
strategy = create_reasoning_strategy("openai", model="o3")
test_suite = create_test_suite(config_file="config/test_scenarios.json", tags=["weather", "math"])
analyzer = CombinedAnalyzer()

# Run tests
tester = ModelPerformanceTester(strategy, test_suite, analyzer)
results = tester.run_tests()
analysis = tester.analyze_results()
output_file = tester.save_results()
```

## Available Components

### Reasoning Strategies
- `openai`: OpenAI API integration (o3, o1, gpt-4, etc.)
- `custom`: Rule-based keyword matching system

### Test Scenarios (via config files)
- **General scenarios** (`config/test_scenarios.json`):
  - Single tool calls (weather, math, search)
  - Multiple tool calls 
  - No tool needed scenarios
  - Tool selection challenges
- **Trading scenarios** (`config/trading_scenarios.json`):
  - Price checking and charts
  - Order entry (market, limit, stop)
  - Options chains and analysis
  - Portfolio and account management

## Results & Analysis

Every test execution captures:

```json
{
  "scenario_name": "Simple Weather Query",
  "success": true,
  "latency_ms": 234.56,
  "actual_tool_calls": [{"name": "get_weather", "arguments": {"location": "San Francisco, CA"}}],
  "expected_tool_calls": [{"name": "get_weather", "arguments": {"location": "San Francisco, CA"}}],
  "validation_details": {"matches_expected": true},
  "tokens_used": {"prompt_tokens": 45, "completion_tokens": 32, "total_tokens": 77}
}
```

Analysis includes:
- **Accuracy**: Success rates, tool usage patterns, failure analysis
- **Latency**: Response time statistics, percentiles, distributions  
- **Efficiency**: Token usage, cost analysis
- **Scenario Breakdown**: Performance by test type

## Configuration

### Test Scenarios
Configure test scenarios in JSON files:

```json
{
  "scenarios": [
    {
      "name": "Weather Query",
      "prompt": "What's the weather in Paris?",
      "tools": [...],
      "expected_tool_calls": [...],
      "tags": ["weather", "simple"]
    }
  ]
}
```

### Custom Strategies
Extend the `BaseReasoningStrategy` class:

```python
from reasoning_strategies.base_strategy import BaseReasoningStrategy
from tool_params.tool_definitions import TestScenario, ExecutionResult

class MyCustomStrategy(BaseReasoningStrategy):
    def execute_scenario(self, scenario: TestScenario) -> ExecutionResult:
        # Your custom logic here
        return ExecutionResult(...)
```

## Migration from Old System

The old system had separate files for different test types:
- `tool_call_latency_demo.py` → Now handled by any test with latency measurement
- `tool_call_accuracy_test.py` → `config/test_scenarios.json` + `base_test_suite.py`  
- `trading_terminal_test.py` → `config/trading_scenarios.json` + `base_test_suite.py`
- `analyze_trading_results.py` → `analyzers/combined_analyzer.py`

**Key improvements:**
- ✅ Composable: Mix any strategy with any scenario configuration
- ✅ Unified analysis: All metrics in one place
- ✅ Extensible: Easy to add new strategies and scenario types
- ✅ Configuration-driven: No hardcoded test suite classes
- ✅ No duplication: Single test suite handles all scenario types

## Examples

See `example_usage.py` for complete examples of:
- OpenAI strategy with default scenarios
- Custom strategy with trading scenarios from config file
- Viewing strategy capabilities and test suite information

## Requirements

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"  # For OpenAI strategy
``` 