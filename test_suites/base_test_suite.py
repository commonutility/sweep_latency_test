"""
Configurable test suite that loads scenarios from files
"""

import os
import json
from typing import List, Dict, Any, Optional
from tool_params.tool_definitions import TestScenario, ExecutionResult, ValidationResult, ToolDefinition
from .validation import validate_tool_calls
from tool_params.tool_definitions import get_weather_tool, get_calculator_tool, get_search_tool


class BaseTestSuite:
    """
    Configurable test suite that loads scenarios from JSON files
    
    This test suite can load any type of scenario from configuration files,
    making it flexible enough to handle different domains (accuracy testing,
    trading scenarios, etc.) without needing separate test suite classes.
    """
    
    def __init__(self, name: str = "ConfigurableTestSuite", config_file: Optional[str] = None, 
                 tags: Optional[List[str]] = None, verbose: bool = False):
        self.name = name
        self.verbose = verbose
        self.config_file = config_file or "config/test_scenarios.json"
        self.filter_tags = tags
        self._scenarios: List[TestScenario] = []
    
    def load_scenarios(self) -> List[TestScenario]:
        """
        Load test scenarios from config file or use defaults
        
        Returns:
            List of TestScenario objects
        """
        # Try to load from config file first
        if os.path.exists(self.config_file):
            try:
                scenarios = self._load_from_config_file()
                if self.verbose:
                    print(f"Loaded {len(scenarios)} scenarios from {self.config_file}")
                return scenarios
            except Exception as e:
                if self.verbose:
                    print(f"Failed to load from config file: {e}")
                    print("Using default scenarios instead")
        
        # Fall back to default scenarios
        scenarios = self._get_default_scenarios()
        if self.verbose:
            print(f"Using {len(scenarios)} default scenarios")
        
        return scenarios
    
    def _load_from_config_file(self) -> List[TestScenario]:
        """Load scenarios from JSON configuration file"""
        
        with open(self.config_file, 'r') as f:
            data = json.load(f)
        
        scenarios = []
        for scenario_data in data.get("scenarios", []):
            # Convert tools from dict format to ToolDefinition objects
            tools = []
            for tool_data in scenario_data.get("tools", []):
                tools.append(ToolDefinition(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    parameters=tool_data["parameters"]
                ))
            
            scenario = TestScenario(
                name=scenario_data["name"],
                description=scenario_data.get("description", ""),
                prompt=scenario_data["prompt"],
                tools=tools,
                expected_tool_calls=scenario_data.get("expected_tool_calls", []),
                tags=scenario_data.get("tags", [])
            )
            
            # Apply tag filtering if specified
            if self.filter_tags:
                if any(tag in scenario.tags for tag in self.filter_tags):
                    scenarios.append(scenario)
            else:
                scenarios.append(scenario)
        
        return scenarios
    
    def _get_default_scenarios(self) -> List[TestScenario]:
        """Get default test scenarios covering common tool calling patterns"""
        
        # Get common tools
        weather_tool = get_weather_tool()
        calculator_tool = get_calculator_tool()
        search_tool = get_search_tool()
        
        scenarios = [
            # Basic single tool scenarios
            TestScenario(
                name="Simple Weather Query",
                description="Test basic weather tool usage",
                prompt="What's the weather in San Francisco?",
                tools=[weather_tool],
                expected_tool_calls=[
                    {"name": "get_weather", "arguments": {"location": "San Francisco, CA"}}
                ],
                tags=["weather", "simple", "single_tool"]
            ),
            
            TestScenario(
                name="Simple Math Calculation",
                description="Test basic calculation",
                prompt="What is 15 * 23?",
                tools=[calculator_tool],
                expected_tool_calls=[
                    {"name": "calculate", "arguments": {"expression": "15 * 23"}}
                ],
                tags=["math", "simple", "single_tool"]
            ),
            
            TestScenario(
                name="Web Search Query",
                description="Test web search functionality",
                prompt="Search for information about Python programming",
                tools=[search_tool],
                expected_tool_calls=[
                    {"name": "search_web", "arguments": {"query": "Python programming"}}
                ],
                tags=["search", "simple", "single_tool"]
            ),
            
            # Multiple tool scenarios
            TestScenario(
                name="Mixed Tools Request",
                description="Test using different tools in one request",
                prompt="What's the weather in London and what's 50 divided by 7?",
                tools=[weather_tool, calculator_tool],
                expected_tool_calls=[
                    {"name": "get_weather", "arguments": {"location": "London, UK"}},
                    {"name": "calculate", "arguments": {"expression": "50 / 7"}}
                ],
                tags=["mixed", "multiple", "different_tools"]
            ),
            
            # No tool needed scenarios
            TestScenario(
                name="No Tool Needed",
                description="Test when no tool should be called",
                prompt="Tell me a joke about programmers",
                tools=[weather_tool, calculator_tool, search_tool],
                expected_tool_calls=[],
                tags=["no_tool", "direct_response"]
            )
        ]
        
        # Apply tag filtering if specified
        if self.filter_tags:
            scenarios = [s for s in scenarios if any(tag in s.tags for tag in self.filter_tags)]
        
        return scenarios
    
    def get_scenarios(self, tags: Optional[List[str]] = None) -> List[TestScenario]:
        """
        Get test scenarios, optionally filtered by tags
        
        Args:
            tags: Optional list of tags to filter by
            
        Returns:
            List of TestScenario objects
        """
        if not self._scenarios:
            self._scenarios = self.load_scenarios()
        
        if tags:
            return [s for s in self._scenarios if any(tag in s.tags for tag in tags)]
        return self._scenarios
    
    def validate_result(self, scenario: TestScenario, result: ExecutionResult) -> ValidationResult:
        """
        Validate an execution result against the expected outcome
        
        Args:
            scenario: The test scenario that was executed
            result: The execution result to validate
            
        Returns:
            ValidationResult with validation details
        """
        if not result.success:
            # If execution failed, validation fails too
            return ValidationResult(
                scenario_name=scenario.name,
                success=False,
                latency_ms=result.latency_ms,
                actual_tool_calls=result.actual_tool_calls,
                expected_tool_calls=scenario.expected_tool_calls,
                validation_details={"error": result.error, "reason": "Execution failed"},
                error=result.error,
                model_response=result.model_response,
                tokens_used=result.tokens_used,
                metadata=result.metadata
            )
        
        # Use custom validator if provided, otherwise use default
        validation_details = validate_tool_calls(
            actual=result.actual_tool_calls or [],
            expected=scenario.expected_tool_calls,
            custom_validator=scenario.validation_function
        )
        
        return ValidationResult(
            scenario_name=scenario.name,
            success=validation_details.get("matches_expected", False),
            latency_ms=result.latency_ms,
            actual_tool_calls=result.actual_tool_calls,
            expected_tool_calls=scenario.expected_tool_calls,
            validation_details=validation_details,
            error=result.error,
            model_response=result.model_response,
            tokens_used=result.tokens_used,
            metadata=result.metadata
        )
    
    def get_test_info(self) -> Dict[str, Any]:
        """
        Get information about this test suite
        
        Returns:
            Dict with information about the test suite
        """
        scenarios = self.get_scenarios()
        tags = set()
        for scenario in scenarios:
            tags.update(scenario.tags)
        
        return {
            "name": self.name,
            "total_scenarios": len(scenarios),
            "available_tags": sorted(list(tags)),
            "description": self.__doc__ or "No description available"
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        return self.__str__() 