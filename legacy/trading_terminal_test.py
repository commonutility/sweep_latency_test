#!/usr/bin/env python3
"""
Trading Terminal Tool Call Testing
Tests model's ability to make appropriate UI tool calls for trading operations
"""

import os
from datetime import datetime
from tool_call_accuracy_test import (
    ToolCallAccuracyTester,
    ToolDefinition,
    TestScenario
)

# Define Trading Terminal UI Tools
def get_trading_ui_tools():
    """Define all available UI tools for the trading terminal"""
    
    price_pane_tool = ToolDefinition(
        name="render_price_pane",
        description="Display real-time price information for an asset",
        parameters={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The asset symbol (e.g., AAPL, BTC-USD, ES)"
                },
                "timeframe": {
                    "type": "string",
                    "enum": ["1m", "5m", "15m", "1h", "1d", "1w"],
                    "description": "Chart timeframe",
                    "default": "5m"
                },
                "chart_type": {
                    "type": "string",
                    "enum": ["candlestick", "line", "bar"],
                    "description": "Type of price chart",
                    "default": "candlestick"
                }
            },
            "required": ["symbol"]
        }
    )
    
    orderbook_tool = ToolDefinition(
        name="render_orderbook_pane",
        description="Display order book with bid/ask levels for an asset",
        parameters={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The asset symbol"
                },
                "depth": {
                    "type": "integer",
                    "description": "Number of price levels to show",
                    "default": 10
                },
                "aggregation": {
                    "type": "number",
                    "description": "Price level aggregation (e.g., 0.01 for $0.01 increments)",
                    "default": 0.01
                }
            },
            "required": ["symbol"]
        }
    )
    
    order_entry_tool = ToolDefinition(
        name="open_order_entry",
        description="Open order entry form for placing trades",
        parameters={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The asset symbol to trade"
                },
                "side": {
                    "type": "string",
                    "enum": ["buy", "sell"],
                    "description": "Order side"
                },
                "order_type": {
                    "type": "string",
                    "enum": ["market", "limit", "stop", "stop_limit"],
                    "description": "Type of order",
                    "default": "limit"
                },
                "quantity": {
                    "type": "number",
                    "description": "Number of units/contracts"
                },
                "price": {
                    "type": "number",
                    "description": "Limit price (required for limit orders)"
                },
                "stop_price": {
                    "type": "number",
                    "description": "Stop price (required for stop orders)"
                },
                "time_in_force": {
                    "type": "string",
                    "enum": ["GTC", "IOC", "FOK", "DAY"],
                    "description": "Order time in force",
                    "default": "DAY"
                }
            },
            "required": ["symbol", "side", "order_type", "quantity"]
        }
    )
    
    positions_tool = ToolDefinition(
        name="render_positions_pane",
        description="Display current positions and P&L",
        parameters={
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "enum": ["all", "open", "closed", "profitable", "losing"],
                    "description": "Filter positions to display",
                    "default": "open"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["symbol", "pnl", "size", "entry_time"],
                    "description": "Sort positions by",
                    "default": "pnl"
                }
            }
        }
    )
    
    options_chain_tool = ToolDefinition(
        name="render_options_chain",
        description="Display options chain for derivatives trading",
        parameters={
            "type": "object",
            "properties": {
                "underlying_symbol": {
                    "type": "string",
                    "description": "The underlying asset symbol"
                },
                "expiration": {
                    "type": "string",
                    "description": "Options expiration date (YYYY-MM-DD) or relative (e.g., 'next_friday', '30_days')"
                },
                "strike_range": {
                    "type": "object",
                    "properties": {
                        "min": {"type": "number"},
                        "max": {"type": "number"}
                    },
                    "description": "Range of strike prices to display"
                },
                "option_type": {
                    "type": "string",
                    "enum": ["calls", "puts", "both"],
                    "description": "Type of options to show",
                    "default": "both"
                }
            },
            "required": ["underlying_symbol"]
        }
    )
    
    market_scanner_tool = ToolDefinition(
        name="open_market_scanner",
        description="Open market scanner to find trading opportunities",
        parameters={
            "type": "object",
            "properties": {
                "scan_type": {
                    "type": "string",
                    "enum": ["volume_leaders", "gainers", "losers", "unusual_options", "breakouts"],
                    "description": "Type of market scan"
                },
                "market": {
                    "type": "string",
                    "enum": ["stocks", "options", "futures", "crypto", "forex"],
                    "description": "Market to scan"
                },
                "filters": {
                    "type": "object",
                    "properties": {
                        "min_price": {"type": "number"},
                        "max_price": {"type": "number"},
                        "min_volume": {"type": "number"},
                        "min_market_cap": {"type": "number"}
                    }
                }
            },
            "required": ["scan_type", "market"]
        }
    )
    
    technical_analysis_tool = ToolDefinition(
        name="add_technical_indicators",
        description="Add technical indicators to the current chart",
        parameters={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Symbol of the chart to add indicators to"
                },
                "indicators": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["SMA", "EMA", "RSI", "MACD", "BB", "VWAP", "ATR", "Volume"],
                                "description": "Indicator type"
                            },
                            "period": {
                                "type": "integer",
                                "description": "Period for the indicator"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Additional parameters specific to the indicator"
                            }
                        },
                        "required": ["type"]
                    }
                }
            },
            "required": ["symbol", "indicators"]
        }
    )
    
    account_summary_tool = ToolDefinition(
        name="render_account_summary",
        description="Display account balance, buying power, and margin information",
        parameters={
            "type": "object",
            "properties": {
                "account_type": {
                    "type": "string",
                    "enum": ["cash", "margin", "futures", "all"],
                    "description": "Type of account to display",
                    "default": "all"
                },
                "show_details": {
                    "type": "boolean",
                    "description": "Show detailed breakdown",
                    "default": True
                }
            }
        }
    )
    
    return [
        price_pane_tool,
        orderbook_tool,
        order_entry_tool,
        positions_tool,
        options_chain_tool,
        market_scanner_tool,
        technical_analysis_tool,
        account_summary_tool
    ]

def get_trading_test_scenarios():
    """Create realistic trading scenarios"""
    tools = get_trading_ui_tools()
    
    scenarios = [
        # Basic Price Checking
        TestScenario(
            name="Check Stock Price",
            description="User wants to see current price of a stock",
            prompt="What's the price of AAPL?",
            tools=tools,
            expected_tool_calls=[
                {"name": "render_price_pane", "arguments": {"symbol": "AAPL"}}
            ],
            tags=["price", "basic", "stocks"]
        ),
        
        TestScenario(
            name="Check Crypto Price with Timeframe",
            description="User wants specific timeframe for crypto",
            prompt="Show me Bitcoin price on the hourly chart",
            tools=tools,
            expected_tool_calls=[
                {"name": "render_price_pane", "arguments": {"symbol": "BTC-USD", "timeframe": "1h"}}
            ],
            tags=["price", "crypto", "timeframe"]
        ),
        
        # Order Entry Scenarios
        TestScenario(
            name="Buy Stock Market Order",
            description="User wants to buy stock at market",
            prompt="Buy 100 shares of TSLA",
            tools=tools,
            expected_tool_calls=[
                {"name": "open_order_entry", "arguments": {
                    "symbol": "TSLA",
                    "side": "buy",
                    "order_type": "market",
                    "quantity": 100
                }}
            ],
            tags=["order", "buy", "market", "stocks"]
        ),
        
        TestScenario(
            name="Buy Futures Contracts",
            description="User wants to buy futures contracts",
            prompt="Buy 400 futures of ES",
            tools=tools,
            expected_tool_calls=[
                {"name": "open_order_entry", "arguments": {
                    "symbol": "ES",
                    "side": "buy",
                    "order_type": "market",
                    "quantity": 400
                }}
            ],
            tags=["order", "buy", "futures"]
        ),
        
        TestScenario(
            name="Sell with Limit Order",
            description="User wants to place a limit sell order",
            prompt="Sell 50 shares of GOOGL at $150",
            tools=tools,
            expected_tool_calls=[
                {"name": "open_order_entry", "arguments": {
                    "symbol": "GOOGL",
                    "side": "sell",
                    "order_type": "limit",
                    "quantity": 50,
                    "price": 150
                }}
            ],
            tags=["order", "sell", "limit", "stocks"]
        ),
        
        # Options Trading
        TestScenario(
            name="View Options Chain",
            description="User wants to see options for a stock",
            prompt="Show me long dated options for SPY",
            tools=tools,
            expected_tool_calls=[
                {"name": "render_options_chain", "arguments": {
                    "underlying_symbol": "SPY",
                    "expiration": "30_days"
                }}
            ],
            tags=["options", "chain"]
        ),
        
        TestScenario(
            name="Options with Specific Expiry",
            description="User wants options with specific expiration",
            prompt="Get 200 long dated contracts for NVDA expiring in January",
            tools=tools,
            expected_tool_calls=[
                {"name": "render_options_chain", "arguments": {
                    "underlying_symbol": "NVDA",
                    "expiration": "next_january"
                }}
            ],
            tags=["options", "specific_expiry"]
        ),
        
        # Market Analysis
        TestScenario(
            name="View Order Book",
            description="User wants to see market depth",
            prompt="Show me the order book for MSFT",
            tools=tools,
            expected_tool_calls=[
                {"name": "render_orderbook_pane", "arguments": {"symbol": "MSFT"}}
            ],
            tags=["orderbook", "analysis"]
        ),
        
        TestScenario(
            name="Check Positions",
            description="User wants to see their positions",
            prompt="Show my current positions",
            tools=tools,
            expected_tool_calls=[
                {"name": "render_positions_pane", "arguments": {"filter": "open"}}
            ],
            tags=["positions", "portfolio"]
        ),
        
        TestScenario(
            name="Find Trading Opportunities",
            description="User wants to scan for opportunities",
            prompt="Find me the top volume stocks today",
            tools=tools,
            expected_tool_calls=[
                {"name": "open_market_scanner", "arguments": {
                    "scan_type": "volume_leaders",
                    "market": "stocks"
                }}
            ],
            tags=["scanner", "opportunities"]
        ),
        
        # Technical Analysis
        TestScenario(
            name="Add Simple Indicator",
            description="User wants to add technical indicator",
            prompt="Add a 50-day moving average to AAPL chart",
            tools=tools,
            expected_tool_calls=[
                {"name": "add_technical_indicators", "arguments": {
                    "symbol": "AAPL",
                    "indicators": [{"type": "SMA", "period": 50}]
                }}
            ],
            tags=["technical", "indicators"]
        ),
        
        TestScenario(
            name="Multiple Indicators",
            description="User wants multiple indicators",
            prompt="Add RSI and MACD to the Tesla chart",
            tools=tools,
            expected_tool_calls=[
                {"name": "add_technical_indicators", "arguments": {
                    "symbol": "TSLA",
                    "indicators": [
                        {"type": "RSI", "period": 14},
                        {"type": "MACD"}
                    ]
                }}
            ],
            tags=["technical", "multiple_indicators"]
        ),
        
        # Complex Multi-Tool Scenarios
        TestScenario(
            name="Price Check Before Order",
            description="User wants to see price then place order",
            prompt="Show me AMZN price and prepare to buy 25 shares",
            tools=tools,
            expected_tool_calls=[
                {"name": "render_price_pane", "arguments": {"symbol": "AMZN"}},
                {"name": "open_order_entry", "arguments": {
                    "symbol": "AMZN",
                    "side": "buy",
                    "order_type": "market",
                    "quantity": 25
                }}
            ],
            tags=["multi_tool", "price_order"]
        ),
        
        TestScenario(
            name="Full Analysis Setup",
            description="User wants comprehensive view",
            prompt="I want to analyze META - show me the price chart, order book, and add volume indicators",
            tools=tools,
            expected_tool_calls=[
                {"name": "render_price_pane", "arguments": {"symbol": "META"}},
                {"name": "render_orderbook_pane", "arguments": {"symbol": "META"}},
                {"name": "add_technical_indicators", "arguments": {
                    "symbol": "META",
                    "indicators": [{"type": "Volume"}]
                }}
            ],
            tags=["multi_tool", "analysis", "comprehensive"]
        ),
        
        # Account Management
        TestScenario(
            name="Check Account Balance",
            description="User wants to see account information",
            prompt="Show me my account balance",
            tools=tools,
            expected_tool_calls=[
                {"name": "render_account_summary", "arguments": {}}
            ],
            tags=["account", "balance"]
        ),
        
        # Edge Cases
        TestScenario(
            name="Ambiguous Symbol",
            description="User uses ambiguous reference",
            prompt="Buy Apple",
            tools=tools,
            expected_tool_calls=[
                {"name": "open_order_entry", "arguments": {
                    "symbol": "AAPL",
                    "side": "buy",
                    "order_type": "market",
                    "quantity": 1  # Default to 1 when not specified
                }}
            ],
            tags=["edge_case", "ambiguous"]
        ),
        
        TestScenario(
            name="Stop Loss Order",
            description="User wants to place stop loss",
            prompt="Set a stop loss at $95 for my 100 shares of DIS",
            tools=tools,
            expected_tool_calls=[
                {"name": "open_order_entry", "arguments": {
                    "symbol": "DIS",
                    "side": "sell",
                    "order_type": "stop",
                    "quantity": 100,
                    "stop_price": 95
                }}
            ],
            tags=["order", "stop_loss", "risk_management"]
        )
    ]
    
    return scenarios

def custom_trading_validator(actual, expected):
    """Custom validator for trading scenarios that's more flexible"""
    if len(actual) != len(expected):
        return {
            "matches_expected": False,
            "reason": f"Expected {len(expected)} tool calls, got {len(actual)}"
        }
    
    for i, (act, exp) in enumerate(zip(actual, expected)):
        if act["name"] != exp["name"]:
            return {
                "matches_expected": False,
                "reason": f"Tool name mismatch at position {i}: expected '{exp['name']}', got '{act['name']}'"
            }
        
        # For trading, be flexible with symbol formats (AAPL vs aapl)
        act_args = act.get("arguments", {})
        exp_args = exp.get("arguments", {})
        
        if "symbol" in act_args and "symbol" in exp_args:
            if act_args["symbol"].upper() != exp_args["symbol"].upper():
                return {
                    "matches_expected": False,
                    "reason": f"Symbol mismatch: expected '{exp_args['symbol']}', got '{act_args['symbol']}'"
                }
            # Normalize symbols for comparison
            act_args = act_args.copy()
            exp_args = exp_args.copy()
            act_args["symbol"] = act_args["symbol"].upper()
            exp_args["symbol"] = exp_args["symbol"].upper()
        
        # Check other required fields
        for key in exp_args:
            if key not in act_args:
                return {
                    "matches_expected": False,
                    "reason": f"Missing required argument '{key}' in tool call {i}"
                }
            
            # Be flexible with numeric values (100 vs 100.0)
            if isinstance(exp_args[key], (int, float)) and isinstance(act_args[key], (int, float)):
                if abs(exp_args[key] - act_args[key]) > 0.01:
                    return {
                        "matches_expected": False,
                        "reason": f"Numeric value mismatch for '{key}': expected {exp_args[key]}, got {act_args[key]}"
                    }
            elif exp_args[key] != act_args[key]:
                return {
                    "matches_expected": False,
                    "reason": f"Argument mismatch for '{key}': expected '{exp_args[key]}', got '{act_args[key]}'"
                }
    
    return {"matches_expected": True}

def main():
    """Run trading terminal tool call tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test trading terminal tool calls")
    parser.add_argument("--model", default="o3", help="Model to test")
    parser.add_argument("--tags", nargs="+", help="Filter by tags")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Check API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    # Get test scenarios
    scenarios = get_trading_test_scenarios()
    
    # Add custom validator to all scenarios
    for scenario in scenarios:
        scenario.validation_function = custom_trading_validator
    
    # Create tester
    tester = ToolCallAccuracyTester(model=args.model, verbose=args.verbose)
    
    # Run tests
    print("=" * 60)
    print("Trading Terminal Tool Call Tests")
    print("=" * 60)
    print()
    
    if args.tags:
        scenarios = [s for s in scenarios if any(tag in s.tags for tag in args.tags)]
        print(f"Running scenarios with tags: {args.tags}")
    
    summary = tester.run_test_suite(scenarios)
    
    # Print category breakdown
    print("\n" + "=" * 60)
    print("RESULTS BY CATEGORY")
    print("=" * 60)
    
    categories = {}
    for result in tester.results:
        scenario = next(s for s in scenarios if s.name == result.scenario_name)
        for tag in scenario.tags:
            if tag not in categories:
                categories[tag] = {"total": 0, "passed": 0}
            categories[tag]["total"] += 1
            if result.success:
                categories[tag]["passed"] += 1
    
    for category, stats in sorted(categories.items()):
        success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"{category:20} {stats['passed']:2}/{stats['total']:2} ({success_rate:5.1f}%)")
    
    # Save results
    filename = f"trading_terminal_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    tester.save_results(filename)

if __name__ == "__main__":
    main() 