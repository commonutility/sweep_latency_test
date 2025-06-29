#!/usr/bin/env python3
"""
Example usage of the reorganized model performance testing framework
"""

import os
from main import create_reasoning_strategy, create_test_suite, ModelPerformanceTester
from analyzers.combined_analyzer import CombinedAnalyzer


def main():
    """Example of how to use the new composable system"""
    
    # Example 1: Basic usage with OpenAI strategy and default scenarios
    print("Example 1: OpenAI strategy with default scenarios")
    print("=" * 60)
    
    if os.environ.get("OPENAI_API_KEY"):
        # Create components
        strategy = create_reasoning_strategy("openai", model="o3", verbose=True)
        test_suite = create_test_suite(tags=["weather", "math"], verbose=True)
        analyzer = CombinedAnalyzer(verbose=True)
        
        # Create tester and run
        tester = ModelPerformanceTester(strategy, test_suite, analyzer, verbose=True)
        results = tester.run_tests()
        analysis = tester.analyze_results()
        output_file = tester.save_results()
        
        print(f"\nCompleted! Results saved to: {output_file}")
    else:
        print("Skipping OpenAI example - no API key set")
    
    print("\n\n")
    
    # Example 2: Custom strategy with config file scenarios
    print("Example 2: Custom strategy with config file scenarios")
    print("=" * 60)
    
    # Create components
    custom_strategy = create_reasoning_strategy("custom", name="Rule-Based", verbose=True)
    test_suite = create_test_suite(config_file="config/trading_scenarios.json", verbose=True)
    analyzer = CombinedAnalyzer(verbose=True)
    
    # Create tester and run
    tester = ModelPerformanceTester(custom_strategy, test_suite, analyzer, verbose=True)
    results = tester.run_tests()
    analysis = tester.analyze_results()
    output_file = tester.save_results()
    
    print(f"\nCompleted! Results saved to: {output_file}")
    
    print("\n\n")
    
    # Example 3: Show capabilities
    print("Example 3: Strategy capabilities and test suite info")
    print("=" * 60)
    
    strategies = ["openai", "custom"]
    config_files = ["config/test_scenarios.json", "config/trading_scenarios.json"]
    
    for strategy_name in strategies:
        try:
            strategy = create_reasoning_strategy(strategy_name, model="o3")
            capabilities = strategy.get_capabilities()
            print(f"\n{strategy_name.upper()} Strategy Capabilities:")
            for key, value in capabilities.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"\n{strategy_name.upper()} Strategy: {e}")
    
    for config_file in config_files:
        try:
            suite = create_test_suite(config_file=config_file)
            info = suite.get_test_info()
            print(f"\nTest Suite ({config_file}):")
            for key, value in info.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"\nTest Suite ({config_file}): {e}")


if __name__ == "__main__":
    main() 