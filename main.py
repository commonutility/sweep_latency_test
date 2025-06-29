#!/usr/bin/env python3
"""
Main orchestrator for model performance testing
Composable system that runs reasoning strategies against test suites and analyzes results
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reasoning_strategies.base_strategy import BaseReasoningStrategy
from test_suites.base_test_suite import BaseTestSuite
from analyzers.combined_analyzer import CombinedAnalyzer


class ModelPerformanceTester:
    """Main class that orchestrates testing of reasoning strategies against test suites"""
    
    def __init__(self, reasoning_strategy: BaseReasoningStrategy, 
                 test_suite: BaseTestSuite, 
                 analyzer: CombinedAnalyzer,
                 verbose: bool = True):
        self.reasoning_strategy = reasoning_strategy
        self.test_suite = test_suite
        self.analyzer = analyzer
        self.verbose = verbose
        self.results = []
        
    def run_tests(self) -> Dict[str, Any]:
        """Run all tests in the test suite using the reasoning strategy"""
        if self.verbose:
            print("=" * 60)
            print("MODEL PERFORMANCE TESTING")
            print("=" * 60)
            print(f"Strategy: {self.reasoning_strategy.name}")
            print(f"Test Suite: {self.test_suite.name}")
            print(f"Timestamp: {datetime.now().isoformat()}")
            print("=" * 60)
        
        # Get test scenarios from the test suite
        scenarios = self.test_suite.get_scenarios()
        
        if self.verbose:
            print(f"\nRunning {len(scenarios)} scenarios...")
        
        # Run each scenario using the reasoning strategy
        for i, scenario in enumerate(scenarios, 1):
            if self.verbose:
                print(f"\n[{i}/{len(scenarios)}] {scenario.name}")
                print(f"Prompt: {scenario.prompt}")
                print("Running...", end="", flush=True)
            
            # Execute the scenario
            result = self.reasoning_strategy.execute_scenario(scenario)
            
            # Validate the result
            validated_result = self.test_suite.validate_result(scenario, result)
            
            self.results.append(validated_result)
            
            if self.verbose:
                success_indicator = "✓" if validated_result.success else "✗"
                print(f" {success_indicator} ({validated_result.latency_ms:.2f}ms)")
                
                if validated_result.actual_tool_calls:
                    print(f"  Tool calls: {len(validated_result.actual_tool_calls)}")
                    for tc in validated_result.actual_tool_calls:
                        print(f"    - {tc.get('name', 'unknown')}({tc.get('arguments', {})})")
                
                if not validated_result.success:
                    print(f"  ⚠️  Validation failed: {validated_result.validation_details.get('reason', 'Unknown')}")
        
        return self.results
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze the test results"""
        if not self.results:
            print("No results to analyze. Run tests first.")
            return {}
        
        if self.verbose:
            print("\n" + "=" * 60)
            print("ANALYZING RESULTS")
            print("=" * 60)
        
        # Use the analyzer to process results
        analysis = self.analyzer.analyze(
            results=self.results,
            strategy_name=self.reasoning_strategy.name,
            test_suite_name=self.test_suite.name
        )
        
        if self.verbose:
            self.analyzer.print_analysis(analysis)
        
        return analysis
    
    def save_results(self, output_dir: str = "results") -> str:
        """Save results and analysis to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.reasoning_strategy.name}_{self.test_suite.name}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Get analysis
        analysis = self.analyzer.analyze(
            results=self.results,
            strategy_name=self.reasoning_strategy.name,
            test_suite_name=self.test_suite.name
        )
        
        # Save to file
        output_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "reasoning_strategy": self.reasoning_strategy.name,
                "test_suite": self.test_suite.name,
                "total_scenarios": len(self.results)
            },
            "analysis": analysis,
            "detailed_results": [result.to_dict() for result in self.results]
        }
        
        import json
        with open(filepath, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        if self.verbose:
            print(f"\nResults saved to: {filepath}")
        
        return filepath


def create_reasoning_strategy(strategy_name: str, **kwargs) -> BaseReasoningStrategy:
    """Factory function to create reasoning strategies"""
    if strategy_name.lower() == "openai":
        from reasoning_strategies.openai_strategy import OpenAIStrategy
        return OpenAIStrategy(**kwargs)
    elif strategy_name.lower() == "custom":
        from reasoning_strategies.custom_strategy import CustomStrategy
        return CustomStrategy(**kwargs)
    else:
        raise ValueError(f"Unknown reasoning strategy: {strategy_name}")


def create_test_suite(**kwargs) -> BaseTestSuite:
    """Factory function to create a configurable test suite"""
    from test_suites.base_test_suite import BaseTestSuite
    return BaseTestSuite(**kwargs)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Model Performance Testing Framework")
    
    # Strategy selection
    parser.add_argument("--strategy", default="openai", 
                       choices=["openai", "custom"],
                       help="Reasoning strategy to use")
    parser.add_argument("--model", default="o3",
                       help="Model to use (for strategies that support it)")
    
    # Test configuration
    parser.add_argument("--config", 
                       help="Path to test configuration file")
    parser.add_argument("--tags", nargs="*",
                       help="Filter scenarios by tags")
    
    # Output options
    parser.add_argument("--output-dir", default="results",
                       help="Directory to save results")
    parser.add_argument("--verbose", action="store_true", default=True,
                       help="Verbose output")
    parser.add_argument("--quiet", action="store_true",
                       help="Quiet mode (overrides verbose)")
    
    args = parser.parse_args()
    
    if args.quiet:
        args.verbose = False
    
    # Check API key for OpenAI strategy
    if args.strategy == "openai" and not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    try:
        # Create reasoning strategy
        strategy = create_reasoning_strategy(
            args.strategy,
            model=args.model,
            verbose=args.verbose
        )
        
        # Create test suite
        test_suite = create_test_suite(
            config_file=args.config,
            tags=args.tags,
            verbose=args.verbose
        )
        
        # Create analyzer
        analyzer = CombinedAnalyzer(verbose=args.verbose)
        
        # Create tester
        tester = ModelPerformanceTester(
            reasoning_strategy=strategy,
            test_suite=test_suite,
            analyzer=analyzer,
            verbose=args.verbose
        )
        
        # Run tests
        results = tester.run_tests()
        
        # Analyze results
        analysis = tester.analyze_results()
        
        # Save results
        output_file = tester.save_results(args.output_dir)
        
        # Print summary
        if args.verbose:
            print("\n" + "=" * 60)
            print("SUMMARY")
            print("=" * 60)
            print(f"Strategy: {strategy.name}")
            print(f"Test Suite: {test_suite.name}")
            print(f"Config File: {test_suite.config_file}")
            print(f"Total Scenarios: {len(results)}")
            print(f"Success Rate: {analysis.get('accuracy', {}).get('success_rate', 0):.1f}%")
            print(f"Average Latency: {analysis.get('latency', {}).get('average_ms', 0):.2f}ms")
            print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 