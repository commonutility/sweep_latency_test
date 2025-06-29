#!/usr/bin/env python3
"""
Analyze and visualize trading terminal test results
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import glob

def load_latest_results(pattern="trading_terminal_results_*.json"):
    """Load the most recent results file"""
    files = glob.glob(pattern)
    if not files:
        print("No results files found")
        return None
    
    latest_file = max(files, key=os.path.getctime)
    print(f"Loading results from: {latest_file}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def analyze_results(data: Dict):
    """Analyze test results and print insights"""
    
    print("\n" + "=" * 60)
    print("TRADING TERMINAL TEST ANALYSIS")
    print("=" * 60)
    
    summary = data.get("summary", {})
    results = data.get("detailed_results", [])
    
    # Overall Performance
    print(f"\nTest Date: {data.get('timestamp', 'Unknown')}")
    print(f"Model: {data.get('model', 'Unknown')}")
    print(f"\nOverall Performance:")
    print(f"  Total Tests: {summary.get('total_tests', 0)}")
    print(f"  Successful: {summary.get('successful_tests', 0)}")
    print(f"  Failed: {summary.get('failed_tests', 0)}")
    print(f"  Success Rate: {summary.get('success_rate', 0):.1f}%")
    print(f"  Average Latency: {summary.get('average_latency_ms', 0):.2f}ms")
    
    # Analyze by scenario type
    scenario_analysis = {}
    for result in results:
        scenario_name = result.get("scenario_name", "Unknown")
        success = result.get("success", False)
        latency = result.get("latency_ms", 0)
        
        if scenario_name not in scenario_analysis:
            scenario_analysis[scenario_name] = {
                "attempts": 0,
                "successes": 0,
                "total_latency": 0,
                "errors": []
            }
        
        scenario_analysis[scenario_name]["attempts"] += 1
        if success:
            scenario_analysis[scenario_name]["successes"] += 1
        else:
            error = result.get("error") or result.get("validation_details", {}).get("reason", "Unknown error")
            scenario_analysis[scenario_name]["errors"].append(error)
        scenario_analysis[scenario_name]["total_latency"] += latency
    
    # Print scenario analysis
    print("\n" + "-" * 60)
    print("SCENARIO BREAKDOWN")
    print("-" * 60)
    
    for scenario, stats in sorted(scenario_analysis.items()):
        success_rate = (stats["successes"] / stats["attempts"] * 100) if stats["attempts"] > 0 else 0
        avg_latency = stats["total_latency"] / stats["attempts"] if stats["attempts"] > 0 else 0
        
        print(f"\n{scenario}:")
        print(f"  Success Rate: {stats['successes']}/{stats['attempts']} ({success_rate:.1f}%)")
        print(f"  Avg Latency: {avg_latency:.2f}ms")
        
        if stats["errors"] and success_rate < 100:
            print("  Common Errors:")
            # Count unique errors
            error_counts = {}
            for error in stats["errors"]:
                error_type = error.split(":")[0] if ":" in error else error[:50]
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"    - {error_type}: {count} time(s)")
    
    # Analyze tool usage patterns
    print("\n" + "-" * 60)
    print("TOOL USAGE ANALYSIS")
    print("-" * 60)
    
    tool_usage = {}
    tool_success = {}
    
    for result in results:
        expected_calls = result.get("expected_tool_calls", [])
        actual_calls = result.get("actual_tool_calls", [])
        success = result.get("success", False)
        
        for call in expected_calls:
            tool_name = call.get("name", "Unknown")
            tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
            
            if success:
                tool_success[tool_name] = tool_success.get(tool_name, 0) + 1
    
    print("\nExpected Tool Call Frequency:")
    for tool, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True):
        success_count = tool_success.get(tool, 0)
        success_rate = (success_count / count * 100) if count > 0 else 0
        print(f"  {tool:25} {count:3} calls ({success_count:3} successful, {success_rate:5.1f}%)")
    
    # Latency analysis
    print("\n" + "-" * 60)
    print("LATENCY ANALYSIS")
    print("-" * 60)
    
    latencies = [r.get("latency_ms", 0) for r in results if r.get("latency_ms")]
    if latencies:
        print(f"  Min Latency: {min(latencies):.2f}ms")
        print(f"  Max Latency: {max(latencies):.2f}ms")
        print(f"  Avg Latency: {sum(latencies) / len(latencies):.2f}ms")
        
        # Latency buckets
        buckets = {"<50ms": 0, "50-100ms": 0, "100-200ms": 0, "200-500ms": 0, ">500ms": 0}
        for lat in latencies:
            if lat < 50:
                buckets["<50ms"] += 1
            elif lat < 100:
                buckets["50-100ms"] += 1
            elif lat < 200:
                buckets["100-200ms"] += 1
            elif lat < 500:
                buckets["200-500ms"] += 1
            else:
                buckets[">500ms"] += 1
        
        print("\n  Latency Distribution:")
        for bucket, count in buckets.items():
            percentage = (count / len(latencies) * 100) if latencies else 0
            print(f"    {bucket:10} {count:3} ({percentage:5.1f}%)")
    
    # Common failure patterns
    print("\n" + "-" * 60)
    print("COMMON FAILURE PATTERNS")
    print("-" * 60)
    
    failure_patterns = {}
    for result in results:
        if not result.get("success", False):
            validation = result.get("validation_details", {})
            
            if validation.get("missing_tools"):
                failure_patterns["Missing expected tools"] = failure_patterns.get("Missing expected tools", 0) + 1
            if validation.get("extra_tools"):
                failure_patterns["Extra unexpected tools"] = failure_patterns.get("Extra unexpected tools", 0) + 1
            if validation.get("argument_matches"):
                for match in validation.get("argument_matches", []):
                    if not match.get("matches", True):
                        failure_patterns["Incorrect arguments"] = failure_patterns.get("Incorrect arguments", 0) + 1
            if not validation.get("correct_tool_count", True):
                failure_patterns["Wrong number of tools"] = failure_patterns.get("Wrong number of tools", 0) + 1
    
    if failure_patterns:
        for pattern, count in sorted(failure_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern}: {count} occurrences")
    else:
        print("  No failures detected (or all failures are API errors)")
    
    return summary

def compare_results(file1: str, file2: str):
    """Compare two result files"""
    print("\n" + "=" * 60)
    print("COMPARING RESULTS")
    print("=" * 60)
    
    with open(file1, 'r') as f:
        data1 = json.load(f)
    with open(file2, 'r') as f:
        data2 = json.load(f)
    
    summary1 = data1.get("summary", {})
    summary2 = data2.get("summary", {})
    
    print(f"\nFile 1: {file1}")
    print(f"  Model: {data1.get('model', 'Unknown')}")
    print(f"  Success Rate: {summary1.get('success_rate', 0):.1f}%")
    print(f"  Avg Latency: {summary1.get('average_latency_ms', 0):.2f}ms")
    
    print(f"\nFile 2: {file2}")
    print(f"  Model: {data2.get('model', 'Unknown')}")
    print(f"  Success Rate: {summary2.get('success_rate', 0):.1f}%")
    print(f"  Avg Latency: {summary2.get('average_latency_ms', 0):.2f}ms")
    
    # Calculate improvements
    success_diff = summary2.get('success_rate', 0) - summary1.get('success_rate', 0)
    latency_diff = summary2.get('average_latency_ms', 0) - summary1.get('average_latency_ms', 0)
    
    print(f"\nDifferences:")
    print(f"  Success Rate: {'+' if success_diff >= 0 else ''}{success_diff:.1f}%")
    print(f"  Latency: {'+' if latency_diff >= 0 else ''}{latency_diff:.2f}ms")

def main():
    """Main analysis function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze trading terminal test results")
    parser.add_argument("--file", help="Specific results file to analyze")
    parser.add_argument("--compare", nargs=2, help="Compare two result files")
    parser.add_argument("--pattern", default="trading_terminal_results_*.json", 
                       help="File pattern to search for")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_results(args.compare[0], args.compare[1])
    else:
        if args.file:
            with open(args.file, 'r') as f:
                data = json.load(f)
        else:
            data = load_latest_results(args.pattern)
        
        if data:
            analyze_results(data)

if __name__ == "__main__":
    main() 