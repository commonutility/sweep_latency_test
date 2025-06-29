# Tool Call Accuracy Testing Framework

A comprehensive framework for testing OpenAI model tool call accuracy with customizable scenarios, validation, and reporting.

## Features

- **Customizable Test Scenarios**: Define your own tools, prompts, and expected outcomes
- **Flexible Validation**: Built-in validation with support for custom validation functions
- **Tag-based Filtering**: Organize and run tests by categories
- **Detailed Reporting**: Track success rates, latencies, and detailed validation results
- **JSON Configuration**: Load test scenarios from JSON files for easy management
- **Command-line Interface**: Run tests with various options

## Quick Start

### Basic Usage

```bash
# Run with default test scenarios
python tool_call_accuracy_test.py

# Run with verbose output
python tool_call_accuracy_test.py --verbose

# Run only tests with specific tags
python tool_call_accuracy_test.py --tags weather math

# Use a different model
python tool_call_accuracy_test.py --model o4-mini

# Load scenarios from custom config file
python tool_call_accuracy_test.py --config my_tests.json
```

### Creating Custom Test Scenarios

#### Method 1: JSON Configuration File

Create a `test_scenarios.json` file:

```json
{
  "scenarios": [
    {
      "name": "Weather Query",
      "description": "Test weather tool usage",
      "prompt": "What's the weather in Paris?",
      "tools": [
        {
          "name": "get_weather",
          "description": "Get weather information",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "City name"
              }
            },
            "required": ["location"]
          }
        }
      ],
      "expected_tool_calls": [
        {
          "name": "get_weather",
          "arguments": {
            "location": "Paris"
          }
        }
      ],
      "tags": ["weather", "simple"]
    }
  ]
}
```

#### Method 2: Python Code

```python
from tool_call_accuracy_test import (
    ToolCallAccuracyTester,
    ToolDefinition,
    TestScenario
)

# Define a tool
calculator_tool = ToolDefinition(
    name="calculate",
    description="Perform calculations",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression"
            }
        },
        "required": ["expression"]
    }
)

# Create a test scenario
scenario = TestScenario(
    name="Simple Math",
    description="Test calculation",
    prompt="What is 2 + 2?",
    tools=[calculator_tool],
    expected_tool_calls=[
        {"name": "calculate", "arguments": {"expression": "2 + 2"}}
    ],
    tags=["math"]
)

# Run the test
tester = ToolCallAccuracyTester(model="o3")
result = tester.run_test(scenario)
```

## Advanced Features

### Custom Validation Functions

Create custom validators for more flexible matching:

```python
def flexible_location_validator(actual, expected):
    """Custom validator that's more flexible with location names"""
    # Your validation logic here
    return {
        "matches_expected": True,  # or False
        "details": "Custom validation passed"
    }

scenario = TestScenario(
    name="Weather Test",
    prompt="Weather in NYC?",
    tools=[weather_tool],
    expected_tool_calls=[...],
    validation_function=flexible_location_validator
)
```

### Running Test Suites

```python
# Load and run all scenarios
scenarios = load_test_scenarios("test_scenarios.json")
tester = ToolCallAccuracyTester(model="o3", verbose=True)
summary = tester.run_test_suite(scenarios)

# Filter by tags
summary = tester.run_test_suite(scenarios, tags=["weather", "simple"])
```

### Analyzing Results

Results are automatically saved to JSON files with detailed information:

```json
{
  "timestamp": "2024-12-17T10:30:00",
  "model": "o3",
  "summary": {
    "total_tests": 10,
    "successful_tests": 8,
    "failed_tests": 2,
    "success_rate": 80.0,
    "average_latency_ms": 125.5
  },
  "detailed_results": [...]
}
```

## Test Scenario Components

### ToolDefinition
- `name`: Tool identifier
- `description`: What the tool does
- `parameters`: JSON Schema for tool parameters

### TestScenario
- `name`: Test identifier
- `description`: Test purpose
- `prompt`: User input to test
- `tools`: List of available tools
- `expected_tool_calls`: Expected model behavior
- `validation_function`: Optional custom validator
- `tags`: Categories for filtering

### TestResult
- `scenario_name`: Which test was run
- `success`: Pass/fail status
- `latency_ms`: Response time
- `actual_tool_calls`: What the model actually did
- `expected_tool_calls`: What was expected
- `validation_details`: Why it passed/failed

## Command-line Options

- `--model MODEL`: Specify the model to test (default: o3)
- `--config FILE`: Load scenarios from JSON file
- `--tags TAG1 TAG2`: Filter tests by tags
- `--verbose`: Show detailed output during testing
- `--output FILE`: Specify output filename for results

## Examples

See `custom_test_example.py` for a complete example of creating custom tools and scenarios for testing stock prices and news queries.

## Tips for Writing Good Tests

1. **Be Specific**: Clear prompts lead to more predictable tool calls
2. **Test Edge Cases**: Include ambiguous prompts to test model judgment
3. **Use Tags**: Organize tests by category for easier management
4. **Validate Flexibly**: Consider variations in how models might format responses
5. **Test Combinations**: Include scenarios with multiple tools and tool calls

## Output Files

The framework generates timestamped JSON files containing:
- Complete test configuration
- Detailed results for each scenario
- Summary statistics
- Token usage information
- Validation details for failed tests 