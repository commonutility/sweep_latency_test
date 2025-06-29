#!/usr/bin/env python3
"""
Example of using the tool call accuracy tester with custom scenarios
"""

import os
from tool_call_accuracy_test import (
    ToolCallAccuracyTester, 
    ToolDefinition, 
    TestScenario
)

# Custom validation function example
def validate_location_format(actual, expected):
    """Custom validator that's more flexible with location formatting"""
    if len(actual) != len(expected):
        return {"matches_expected": False, "reason": "Different number of tool calls"}
    
    for i, (act, exp) in enumerate(zip(actual, expected)):
        if act["name"] != exp["name"]:
            return {"matches_expected": False, "reason": f"Tool name mismatch at index {i}"}
        
        # More flexible location matching
        act_location = act.get("arguments", {}).get("location", "").lower()
        exp_location = exp.get("arguments", {}).get("location", "").lower()
        
        # Remove common variations
        act_location = act_location.replace(",", "").replace(".", "")
        exp_location = exp_location.replace(",", "").replace(".", "")
        
        # Check if the key parts match
        if not all(part in act_location for part in exp_location.split()):
            return {
                "matches_expected": False, 
                "reason": f"Location mismatch: expected '{exp_location}', got '{act_location}'"
            }
    
    return {"matches_expected": True}

def main():
    # Define custom tools
    stock_tool = ToolDefinition(
        name="get_stock_price",
        description="Get the current stock price for a given ticker symbol",
        parameters={
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol, e.g., AAPL, GOOGL"
                },
                "exchange": {
                    "type": "string",
                    "description": "The stock exchange (optional)",
                    "default": "NASDAQ"
                }
            },
            "required": ["ticker"]
        }
    )
    
    news_tool = ToolDefinition(
        name="get_news",
        description="Get recent news articles about a topic",
        parameters={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to search for"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of articles to return",
                    "default": 5
                },
                "time_range": {
                    "type": "string",
                    "enum": ["today", "week", "month"],
                    "description": "Time range for news articles",
                    "default": "week"
                }
            },
            "required": ["topic"]
        }
    )
    
    # Define custom test scenarios
    custom_scenarios = [
        TestScenario(
            name="Stock Price Query",
            description="Test stock price lookup",
            prompt="What's the current price of Apple stock?",
            tools=[stock_tool],
            expected_tool_calls=[
                {"name": "get_stock_price", "arguments": {"ticker": "AAPL"}}
            ],
            tags=["finance", "stocks"]
        ),
        
        TestScenario(
            name="Multiple Stock Prices",
            description="Test multiple stock lookups",
            prompt="Compare the prices of Apple, Google, and Microsoft stocks",
            tools=[stock_tool],
            expected_tool_calls=[
                {"name": "get_stock_price", "arguments": {"ticker": "AAPL"}},
                {"name": "get_stock_price", "arguments": {"ticker": "GOOGL"}},
                {"name": "get_stock_price", "arguments": {"ticker": "MSFT"}}
            ],
            tags=["finance", "stocks", "multiple"]
        ),
        
        TestScenario(
            name="Stock News Combo",
            description="Test combining stock price and news tools",
            prompt="What's Tesla's stock price and any recent news about the company?",
            tools=[stock_tool, news_tool],
            expected_tool_calls=[
                {"name": "get_stock_price", "arguments": {"ticker": "TSLA"}},
                {"name": "get_news", "arguments": {"topic": "Tesla"}}
            ],
            tags=["finance", "news", "combo"]
        ),
        
        TestScenario(
            name="News with Parameters",
            description="Test news tool with specific parameters",
            prompt="Show me 10 articles about AI from this week",
            tools=[news_tool],
            expected_tool_calls=[
                {"name": "get_news", "arguments": {"topic": "AI", "limit": 10, "time_range": "week"}}
            ],
            tags=["news", "parameters"]
        )
    ]
    
    # Create tester instance
    tester = ToolCallAccuracyTester(model="o3", verbose=True)
    
    # Run specific tests
    print("Running custom test scenarios...")
    
    # Run all custom scenarios
    for scenario in custom_scenarios:
        tester.run_test(scenario)
    
    # Or run only scenarios with specific tags
    print("\n\nRunning only 'finance' tagged scenarios...")
    finance_scenarios = [s for s in custom_scenarios if "finance" in s.tags]
    
    tester_filtered = ToolCallAccuracyTester(model="o3", verbose=True)
    summary = tester_filtered.run_test_suite(finance_scenarios)
    
    # Print detailed results
    print("\n" + "=" * 60)
    print("DETAILED RESULTS")
    print("=" * 60)
    
    for result in tester.results:
        print(f"\nScenario: {result.scenario_name}")
        print(f"Success: {result.success}")
        print(f"Latency: {result.latency_ms}ms")
        if result.actual_tool_calls:
            print("Actual tool calls:")
            for tc in result.actual_tool_calls:
                print(f"  - {tc}")
        print(f"Expected tool calls:")
        for tc in result.expected_tool_calls:
            print(f"  - {tc}")
    
    # Save results
    filename = tester.save_results("custom_test_results.json")
    print(f"\nResults saved to: {filename}")

if __name__ == "__main__":
    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    main() 