"""
Custom reasoning strategy implementation
"""

import time
import json
from typing import Dict, Any, List, Optional

from .base_strategy import BaseReasoningStrategy
from tool_params.tool_definitions import TestScenario, ExecutionResult


class CustomStrategy(BaseReasoningStrategy):
    """
    Example custom reasoning strategy
    
    This strategy demonstrates how to implement custom logic for tool calling.
    It uses simple heuristics to determine which tools to call based on keywords
    in the prompt.
    """
    
    def __init__(self, name: str = "Custom", verbose: bool = False, **kwargs):
        super().__init__(name=name, verbose=verbose)
        
        # Custom configuration
        self.latency_simulation = kwargs.get("latency_simulation", True)
        self.min_latency_ms = kwargs.get("min_latency_ms", 50)
        self.max_latency_ms = kwargs.get("max_latency_ms", 200)
        
        # Keyword mappings for tool selection
        self.tool_keywords = {
            "weather": ["weather", "temperature", "forecast", "rain", "sunny", "cloudy"],
            "calculate": ["calculate", "math", "compute", "plus", "minus", "multiply", "divide", "+", "-", "*", "/", "sqrt", "square"],
            "search": ["search", "find", "look up", "google", "information", "news"],
            "email": ["email", "send", "message", "mail"],
            "database": ["database", "query", "orders", "customers", "records"]
        }
    
    def execute_scenario(self, scenario: TestScenario) -> ExecutionResult:
        """Execute a test scenario using custom logic"""
        
        if self.verbose:
            print(f"  Executing with custom strategy: {self.name}")
        
        # Simulate processing time
        start_time = time.time()
        
        try:
            # Analyze the prompt to determine which tools to call
            actual_tool_calls = self._analyze_prompt_and_call_tools(scenario)
            
            # Simulate latency
            if self.latency_simulation:
                import random
                simulated_delay = random.uniform(
                    self.min_latency_ms / 1000, 
                    self.max_latency_ms / 1000
                )
                time.sleep(simulated_delay)
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            return ExecutionResult(
                success=True,
                latency_ms=round(latency_ms, 2),
                actual_tool_calls=actual_tool_calls,
                model_response=f"Custom strategy processed: {scenario.prompt}",
                metadata={
                    "strategy": self.name,
                    "analysis_method": "keyword_matching",
                    "available_tools": [tool.name for tool in scenario.tools]
                }
            )
            
        except Exception as e:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            if self.verbose:
                print(f"  Error executing scenario: {str(e)}")
            
            return ExecutionResult(
                success=False,
                latency_ms=round(latency_ms, 2),
                actual_tool_calls=None,
                error=str(e),
                metadata={
                    "strategy": self.name
                }
            )
    
    def _analyze_prompt_and_call_tools(self, scenario: TestScenario) -> List[Dict[str, Any]]:
        """Analyze the prompt and determine which tools to call"""
        
        prompt_lower = scenario.prompt.lower()
        tool_calls = []
        
        # Create a mapping of available tools
        available_tools = {tool.name: tool for tool in scenario.tools}
        
        # Check for weather-related keywords
        if any(keyword in prompt_lower for keyword in self.tool_keywords.get("weather", [])):
            if "get_weather" in available_tools:
                location = self._extract_location(prompt_lower)
                tool_calls.append({
                    "name": "get_weather",
                    "arguments": {"location": location}
                })
        
        # Check for calculation-related keywords
        if any(keyword in prompt_lower for keyword in self.tool_keywords.get("calculate", [])):
            if "calculate" in available_tools:
                expression = self._extract_math_expression(prompt_lower)
                tool_calls.append({
                    "name": "calculate",
                    "arguments": {"expression": expression}
                })
        
        # Check for search-related keywords
        if any(keyword in prompt_lower for keyword in self.tool_keywords.get("search", [])):
            if "search_web" in available_tools:
                query = self._extract_search_query(prompt_lower)
                tool_calls.append({
                    "name": "search_web",
                    "arguments": {"query": query}
                })
        
        # Check for trading-related tools
        if "render_price_pane" in available_tools:
            symbol = self._extract_symbol(prompt_lower)
            if symbol:
                tool_calls.append({
                    "name": "render_price_pane",
                    "arguments": {"symbol": symbol}
                })
        
        # Check for order entry
        if "open_order_entry" in available_tools:
            order_info = self._extract_order_info(prompt_lower)
            if order_info:
                tool_calls.append({
                    "name": "open_order_entry",
                    "arguments": order_info
                })
        
        return tool_calls
    
    def _extract_location(self, prompt: str) -> str:
        """Extract location from prompt"""
        # Simple heuristics - could be made more sophisticated
        cities = ["san francisco", "new york", "london", "tokyo", "paris", "chicago"]
        for city in cities:
            if city in prompt:
                return city.title()
        return "San Francisco, CA"  # Default
    
    def _extract_math_expression(self, prompt: str) -> str:
        """Extract mathematical expression from prompt"""
        # Look for common patterns
        import re
        
        # Look for "X + Y", "X * Y", etc.
        math_pattern = r'(\d+)\s*([+\-*/])\s*(\d+)'
        match = re.search(math_pattern, prompt)
        if match:
            return f"{match.group(1)} {match.group(2)} {match.group(3)}"
        
        # Look for "square root of X"
        sqrt_pattern = r'square root of (\d+)'
        match = re.search(sqrt_pattern, prompt)
        if match:
            return f"sqrt({match.group(1)})"
        
        return "2 + 2"  # Default
    
    def _extract_search_query(self, prompt: str) -> str:
        """Extract search query from prompt"""
        # Simple extraction - take the prompt as the query
        return prompt.replace("search for", "").replace("find", "").strip()
    
    def _extract_symbol(self, prompt: str) -> Optional[str]:
        """Extract trading symbol from prompt"""
        # Common stock symbols
        symbols = ["aapl", "googl", "msft", "tsla", "amzn", "nvda", "meta", "btc", "eth"]
        for symbol in symbols:
            if symbol in prompt:
                return symbol.upper()
        return None
    
    def _extract_order_info(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Extract order information from prompt"""
        # Simple pattern matching for orders
        import re
        
        # Look for "buy X shares of Y"
        buy_pattern = r'buy (\d+) (?:shares of |contracts? of |)(\w+)'
        match = re.search(buy_pattern, prompt)
        if match:
            return {
                "symbol": match.group(2).upper(),
                "side": "buy",
                "order_type": "market",
                "quantity": int(match.group(1))
            }
        
        # Look for "sell X shares of Y"
        sell_pattern = r'sell (\d+) (?:shares of |contracts? of |)(\w+)'
        match = re.search(sell_pattern, prompt)
        if match:
            return {
                "symbol": match.group(2).upper(),
                "side": "sell",
                "order_type": "market",
                "quantity": int(match.group(1))
            }
        
        return None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return information about this strategy's capabilities"""
        return {
            "name": self.name,
            "provider": "Custom",
            "type": "rule_based",
            "supports_tool_calls": True,
            "supports_streaming": False,
            "keyword_matching": True,
            "latency_simulation": self.latency_simulation,
            "supported_domains": list(self.tool_keywords.keys())
        }
    
    def validate_scenario(self, scenario: TestScenario) -> bool:
        """Check if this strategy can handle the given scenario"""
        # This custom strategy can handle any scenario, but might not be very accurate
        return True
    
    def add_keyword_mapping(self, tool_name: str, keywords: List[str]):
        """Add new keyword mappings for tool selection"""
        self.tool_keywords[tool_name] = keywords
    
    def set_latency_range(self, min_ms: int, max_ms: int):
        """Set the latency simulation range"""
        self.min_latency_ms = min_ms
        self.max_latency_ms = max_ms 