# OpenAI Tool Call Latency Demo

This demo measures the time it takes for OpenAI's o4-mini model to return tool calls in response to various prompts.

## Features

- Measures end-to-end latency for tool call responses
- Tests multiple scenarios:
  - Single tool calls (weather queries, math calculations)
  - Multiple tool calls in one request
  - Prompts that don't require tools
- Provides detailed timing statistics
- Saves results to a timestamped JSON file

## Prerequisites

- Python 3.7+
- OpenAI API key set as environment variable `OPENAI_API_KEY`

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your OpenAI API key is set:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

Run the demo script:
```bash
python tool_call_latency_demo.py
```

## What it measures

The demo measures the complete round-trip time from sending a request to receiving a response, including:
- Network latency
- Model processing time
- Tool call decision making
- Response generation

## Output

The script will:
1. Display real-time results for each test scenario
2. Show summary statistics including average, min, and max latencies
3. Save detailed results to a JSON file with timestamp

## Example Tools

The demo includes two example tools:
- **get_weather**: Simulates a weather information tool
- **calculate**: Simulates a mathematical calculation tool

## Test Scenarios

1. **Weather Query**: Tests a single weather tool call
2. **Math Calculation**: Tests a single calculation tool call
3. **Multiple Tools**: Tests multiple tool calls in one request
4. **No Tool Needed**: Tests response when no tool is required

## Results

Results are saved in JSON format with:
- Individual test results with latencies
- Tool call details
- Token usage information
- Summary statistics

## Note on o4-mini

o4-mini is OpenAI's compact reasoning model released in April 2025. It features:
- 200K token context window
- Multimodal capabilities (text and image)
- Tool support
- Strong performance in math and coding tasks
- Lower cost compared to larger models 