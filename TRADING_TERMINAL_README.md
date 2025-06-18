# Trading Terminal Tool Call Testing Framework

A specialized testing framework for evaluating AI models' ability to make appropriate UI tool calls in a trading terminal context.

## Overview

This framework tests how well AI models can interpret trading commands and translate them into appropriate UI tool calls. Instead of executing trades directly, the model determines which UI components to render or forms to open based on user requests.

## UI Tools Available

### 1. **render_price_pane**
Displays real-time price charts for assets.
- Parameters: symbol, timeframe (1m, 5m, 15m, 1h, 1d, 1w), chart_type (candlestick, line, bar)
- Example: "Show me AAPL price" → Opens price chart for AAPL

### 2. **render_orderbook_pane**
Shows bid/ask levels and market depth.
- Parameters: symbol, depth, aggregation
- Example: "Show me the order book for MSFT" → Displays MSFT order book

### 3. **open_order_entry**
Opens the order entry form for placing trades.
- Parameters: symbol, side (buy/sell), order_type, quantity, price, stop_price, time_in_force
- Example: "Buy 100 shares of TSLA" → Opens order form pre-filled with TSLA buy order

### 4. **render_positions_pane**
Displays current positions and P&L.
- Parameters: filter (all/open/closed/profitable/losing), sort_by
- Example: "Show my positions" → Displays open positions

### 5. **render_options_chain**
Shows options contracts for derivatives trading.
- Parameters: underlying_symbol, expiration, strike_range, option_type
- Example: "Show SPY options" → Displays SPY options chain

### 6. **open_market_scanner**
Opens scanner to find trading opportunities.
- Parameters: scan_type, market, filters
- Example: "Find top volume stocks" → Opens scanner for volume leaders

### 7. **add_technical_indicators**
Adds technical analysis overlays to charts.
- Parameters: symbol, indicators (SMA, EMA, RSI, MACD, etc.)
- Example: "Add RSI to Tesla chart" → Adds RSI indicator

### 8. **render_account_summary**
Shows account balance and margin information.
- Parameters: account_type, show_details
- Example: "Show my balance" → Displays account summary

## Test Scenarios

The framework includes various realistic trading scenarios:

### Basic Operations
- Price checking: "What's the price of AAPL?"
- Simple orders: "Buy 100 shares of TSLA"
- Account info: "Show my account balance"

### Complex Orders
- Limit orders: "Sell 50 GOOGL at $150"
- Stop orders: "Set stop loss at $95 for DIS"
- Time-in-force: "Buy NQ limit 15250 GTC"

### Market Analysis
- Multiple tools: "Show AMZN price and prepare to buy"
- Technical analysis: "Add 50-day MA to AAPL"
- Comprehensive view: "Analyze META - price, orderbook, volume"

### Options Trading
- Chain viewing: "Show long dated SPY options"
- Strike ranges: "QQQ options 380-400 strikes"

### Portfolio Management
- Position filtering: "Show losing positions"
- Risk analysis: "Sort positions by P&L"

## Running Tests

### Basic Usage
```bash
# Run all tests
python trading_terminal_test.py

# Run with specific model
python trading_terminal_test.py --model o4-mini

# Filter by tags
python trading_terminal_test.py --tags order stocks

# Verbose output
python trading_terminal_test.py --verbose
```

### Available Tags
- `order`: Order placement scenarios
- `price`: Price checking scenarios
- `options`: Options trading scenarios
- `technical`: Technical analysis scenarios
- `multi_tool`: Scenarios requiring multiple tools
- `portfolio`: Position and account management
- `analysis`: Market analysis scenarios

## Custom Validation

The framework includes a custom validator that handles:
- Case-insensitive symbol matching (AAPL vs aapl)
- Numeric flexibility (100 vs 100.0)
- Symbol normalization for common variants

## Results Analysis

Results are saved with:
- Success/failure status for each scenario
- Latency measurements
- Actual vs expected tool calls
- Detailed validation reasons
- Category-wise performance breakdown

### Sample Output
```
RESULTS BY CATEGORY
============================================================
order                 15/18 ( 83.3%)
price                  9/10 ( 90.0%)
multi_tool             7/10 ( 70.0%)
technical              8/8  (100.0%)
```

## Extending the Framework

### Adding New Tools
```python
new_tool = ToolDefinition(
    name="render_news_feed",
    description="Display news for an asset",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {"type": "string"},
            "timeframe": {"type": "string"}
        },
        "required": ["symbol"]
    }
)
```

### Adding Test Scenarios
```python
TestScenario(
    name="News Check",
    prompt="Show TSLA news",
    tools=tools,
    expected_tool_calls=[
        {"name": "render_news_feed", "arguments": {"symbol": "TSLA"}}
    ],
    tags=["news", "analysis"]
)
```

## Best Practices

1. **Clear Prompts**: Use natural trading language
2. **Realistic Scenarios**: Test actual trader workflows
3. **Edge Cases**: Include ambiguous requests
4. **Multi-step Operations**: Test complex workflows
5. **Error Scenarios**: Test invalid requests

## Integration

This framework can be integrated into:
- CI/CD pipelines for model validation
- A/B testing different models
- Performance benchmarking
- Trading UI development testing

## Output Files

Results are saved as timestamped JSON files:
- `trading_terminal_results_YYYYMMDD_HHMMSS.json`

Contains:
- Complete test configuration
- Detailed results per scenario
- Performance metrics
- Category breakdowns 