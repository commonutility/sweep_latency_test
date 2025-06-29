"""
Base analyzer interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from tool_params.tool_definitions import ValidationResult


class BaseAnalyzer(ABC):
    """
    Base class for result analyzers
    
    Analyzers process test results and generate insights, statistics,
    and reports about model performance.
    """
    
    def __init__(self, name: str, verbose: bool = False):
        self.name = name
        self.verbose = verbose
    
    @abstractmethod
    def analyze(self, results: List[ValidationResult], 
                strategy_name: str, test_suite_name: str) -> Dict[str, Any]:
        """
        Analyze test results and generate insights
        
        Args:
            results: List of validation results to analyze
            strategy_name: Name of the reasoning strategy used
            test_suite_name: Name of the test suite used
            
        Returns:
            Dict containing analysis results and statistics
        """
        pass
    
    @abstractmethod
    def print_analysis(self, analysis: Dict[str, Any]) -> None:
        """
        Print analysis results in a human-readable format
        
        Args:
            analysis: Analysis results from analyze() method
        """
        pass
    
    def get_analyzer_info(self) -> Dict[str, Any]:
        """
        Get information about this analyzer
        
        Returns:
            Dict with information about the analyzer
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "description": self.__doc__ or "No description available"
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        return self.__str__() 