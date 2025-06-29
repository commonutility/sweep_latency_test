"""
Shared tool definitions and data structures
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Callable
import json


@dataclass
class ToolDefinition:
    """Represents a tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to OpenAI tool format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


@dataclass
class TestScenario:
    """Represents a test scenario"""
    name: str
    description: str
    prompt: str
    tools: List[ToolDefinition]
    expected_tool_calls: List[Dict[str, Any]]  # Expected tool names and arguments
    validation_function: Optional[Callable] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "prompt": self.prompt,
            "tools": [tool.to_dict() for tool in self.tools],
            "expected_tool_calls": self.expected_tool_calls,
            "tags": self.tags
        }


@dataclass
class ExecutionResult:
    """Raw result from executing a reasoning strategy against a scenario"""
    success: bool
    latency_ms: float
    actual_tool_calls: Optional[List[Dict[str, Any]]]
    error: Optional[str] = None
    model_response: Optional[str] = None
    tokens_used: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class ValidationResult:
    """Result after validating an execution result against expected outcomes"""
    scenario_name: str
    success: bool
    latency_ms: float
    actual_tool_calls: Optional[List[Dict[str, Any]]]
    expected_tool_calls: List[Dict[str, Any]]
    validation_details: Dict[str, Any]
    error: Optional[str] = None
    model_response: Optional[str] = None
    tokens_used: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


# Common tool definitions that can be reused across test suites
def get_weather_tool() -> ToolDefinition:
    """Returns the tool definition for getting weather information"""
    return ToolDefinition(
        name="get_weather",
        description="Get the current weather in a given location",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use"
                }
            },
            "required": ["location"]
        }
    )


def get_calculator_tool() -> ToolDefinition:
    """Returns the tool definition for calculating math expressions"""
    return ToolDefinition(
        name="calculate",
        description="Perform a mathematical calculation",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate, e.g. '2 + 2' or 'sqrt(16)'"
                }
            },
            "required": ["expression"]
        }
    )


def get_search_tool() -> ToolDefinition:
    """Returns the tool definition for web search"""
    return ToolDefinition(
        name="search_web",
        description="Search the web for information",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    ) 