"""
Base reasoning strategy interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from tool_params.tool_definitions import TestScenario, ExecutionResult


class BaseReasoningStrategy(ABC):
    """
    Base class for reasoning strategies
    
    A reasoning strategy defines how a model or system processes a test scenario
    and generates tool calls. This could be an API call to OpenAI, Claude, a local
    model, or even a rule-based system.
    """
    
    def __init__(self, name: str, verbose: bool = False):
        self.name = name
        self.verbose = verbose
    
    @abstractmethod
    def execute_scenario(self, scenario: TestScenario) -> ExecutionResult:
        """
        Execute a test scenario and return the result
        
        Args:
            scenario: The test scenario to execute
            
        Returns:
            ExecutionResult containing the outcome of the execution
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return information about this strategy's capabilities
        
        Returns:
            Dict with information about supported features, models, etc.
        """
        pass
    
    def validate_scenario(self, scenario: TestScenario) -> bool:
        """
        Check if this strategy can handle the given scenario
        
        Args:
            scenario: The test scenario to validate
            
        Returns:
            True if the scenario is supported, False otherwise
        """
        # Default implementation - assume all scenarios are supported
        return True
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        return self.__str__() 