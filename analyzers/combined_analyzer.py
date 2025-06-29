"""
Combined analyzer for both accuracy and latency analysis
"""

from typing import List, Dict, Any
import statistics

from .base_analyzer import BaseAnalyzer
from tool_params.tool_definitions import ValidationResult


class CombinedAnalyzer(BaseAnalyzer):
    """
    Combined analyzer that provides both accuracy and latency analysis
    
    This analyzer processes test results to generate comprehensive insights about:
    - Tool call accuracy and success rates
    - Response latency statistics
    - Tool usage patterns
    - Failure analysis
    """
    
    def __init__(self, verbose: bool = False):
        super().__init__(name="Combined", verbose=verbose)
    
    def analyze(self, results: List[ValidationResult], 
                strategy_name: str, test_suite_name: str) -> Dict[str, Any]:
        """Analyze test results and generate comprehensive insights"""
        
        if not results:
            return {"error": "No results to analyze"}
        
        analysis = {
            "metadata": {
                "strategy_name": strategy_name,
                "test_suite_name": test_suite_name,
                "total_results": len(results),
                "timestamp": results[0].metadata.get("timestamp") if results[0].metadata else None
            },
            "accuracy": self._analyze_accuracy(results),
            "latency": self._analyze_latency(results),
            "tool_usage": self._analyze_tool_usage(results),
            "failure_analysis": self._analyze_failures(results),
            "scenario_breakdown": self._analyze_by_scenario(results)
        }
        
        return analysis
    
    def _analyze_accuracy(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Analyze accuracy metrics"""
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - successful_tests
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Analyze by test tags if available
        tag_analysis = {}
        for result in results:
            # Note: We'd need to access scenario tags through metadata or modify data structure
            # For now, we'll skip this detailed analysis
            pass
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": round(success_rate, 1),
            "tag_breakdown": tag_analysis
        }
    
    def _analyze_latency(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Analyze latency metrics"""
        
        latencies = [r.latency_ms for r in results if r.latency_ms is not None]
        
        if not latencies:
            return {"error": "No latency data available"}
        
        # Calculate statistics
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        # Standard deviation if we have enough data points
        stdev_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
        
        # Latency distribution buckets
        buckets = {
            "under_50ms": sum(1 for l in latencies if l < 50),
            "50_100ms": sum(1 for l in latencies if 50 <= l < 100),
            "100_200ms": sum(1 for l in latencies if 100 <= l < 200),
            "200_500ms": sum(1 for l in latencies if 200 <= l < 500),
            "500_1000ms": sum(1 for l in latencies if 500 <= l < 1000),
            "over_1000ms": sum(1 for l in latencies if l >= 1000)
        }
        
        # Percentiles
        percentiles = {
            "p50": statistics.median(latencies),
            "p90": self._percentile(latencies, 0.90),
            "p95": self._percentile(latencies, 0.95),
            "p99": self._percentile(latencies, 0.99)
        }
        
        return {
            "total_measurements": len(latencies),
            "average_ms": round(avg_latency, 2),
            "median_ms": round(median_latency, 2),
            "min_ms": round(min_latency, 2),
            "max_ms": round(max_latency, 2),
            "stdev_ms": round(stdev_latency, 2),
            "percentiles": {k: round(v, 2) for k, v in percentiles.items()},
            "distribution": buckets
        }
    
    def _analyze_tool_usage(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Analyze tool usage patterns"""
        
        tool_stats = {}
        tool_success_stats = {}
        
        for result in results:
            # Analyze expected tool calls
            for expected_call in result.expected_tool_calls:
                tool_name = expected_call.get("name", "unknown")
                
                if tool_name not in tool_stats:
                    tool_stats[tool_name] = {"expected": 0, "actual": 0, "correct": 0}
                    tool_success_stats[tool_name] = []
                
                tool_stats[tool_name]["expected"] += 1
                
                # Check if this tool was actually called correctly
                if result.success and result.actual_tool_calls:
                    for actual_call in result.actual_tool_calls:
                        if actual_call.get("name") == tool_name:
                            tool_stats[tool_name]["actual"] += 1
                            break
                
                # Track success for this specific tool usage
                tool_success_stats[tool_name].append(result.success)
        
        # Calculate success rates per tool
        tool_summary = {}
        for tool_name, stats in tool_stats.items():
            successes = tool_success_stats[tool_name]
            success_rate = (sum(successes) / len(successes) * 100) if successes else 0
            
            tool_summary[tool_name] = {
                "times_expected": stats["expected"],
                "times_called": stats["actual"],
                "success_rate": round(success_rate, 1),
                "accuracy": round((stats["actual"] / stats["expected"] * 100), 1) if stats["expected"] > 0 else 0
            }
        
        return {
            "unique_tools": len(tool_stats),
            "tool_breakdown": tool_summary,
            "most_used": max(tool_stats.keys(), key=lambda k: tool_stats[k]["expected"]) if tool_stats else None,
            "highest_success_rate": max(tool_summary.keys(), key=lambda k: tool_summary[k]["success_rate"]) if tool_summary else None
        }
    
    def _analyze_failures(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Analyze failure patterns"""
        
        failed_results = [r for r in results if not r.success]
        
        if not failed_results:
            return {"total_failures": 0, "failure_rate": 0.0}
        
        # Categorize failures
        failure_categories = {
            "execution_errors": 0,
            "missing_tools": 0,
            "extra_tools": 0,
            "argument_errors": 0,
            "tool_count_mismatch": 0,
            "other": 0
        }
        
        failure_reasons = []
        
        for result in failed_results:
            if result.error:
                failure_categories["execution_errors"] += 1
                failure_reasons.append(f"Execution error: {result.error}")
            elif result.validation_details:
                details = result.validation_details
                reason = details.get("reason", "")
                failure_reasons.append(reason)
                
                if "missing" in reason.lower():
                    failure_categories["missing_tools"] += 1
                elif "extra" in reason.lower():
                    failure_categories["extra_tools"] += 1
                elif "argument" in reason.lower():
                    failure_categories["argument_errors"] += 1
                elif "count" in reason.lower():
                    failure_categories["tool_count_mismatch"] += 1
                else:
                    failure_categories["other"] += 1
            else:
                failure_categories["other"] += 1
                failure_reasons.append("Unknown failure reason")
        
        return {
            "total_failures": len(failed_results),
            "failure_rate": round(len(failed_results) / len(results) * 100, 1),
            "failure_categories": failure_categories,
            "common_reasons": list(set(failure_reasons))[:10]  # Top 10 unique reasons
        }
    
    def _analyze_by_scenario(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Analyze results grouped by scenario"""
        
        scenario_stats = {}
        
        for result in results:
            scenario_name = result.scenario_name
            
            if scenario_name not in scenario_stats:
                scenario_stats[scenario_name] = {
                    "attempts": 0,
                    "successes": 0,
                    "latencies": [],
                    "errors": []
                }
            
            stats = scenario_stats[scenario_name]
            stats["attempts"] += 1
            
            if result.success:
                stats["successes"] += 1
            else:
                error_msg = result.error or result.validation_details.get("reason", "Unknown")
                stats["errors"].append(error_msg)
            
            if result.latency_ms is not None:
                stats["latencies"].append(result.latency_ms)
        
        # Calculate summary statistics for each scenario
        scenario_summary = {}
        for scenario_name, stats in scenario_stats.items():
            success_rate = (stats["successes"] / stats["attempts"] * 100) if stats["attempts"] > 0 else 0
            avg_latency = statistics.mean(stats["latencies"]) if stats["latencies"] else 0
            
            scenario_summary[scenario_name] = {
                "attempts": stats["attempts"],
                "successes": stats["successes"],
                "success_rate": round(success_rate, 1),
                "average_latency_ms": round(avg_latency, 2),
                "unique_errors": len(set(stats["errors"]))
            }
        
        return scenario_summary
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile value"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = percentile * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def print_analysis(self, analysis: Dict[str, Any]) -> None:
        """Print analysis results in a human-readable format"""
        
        print("\n" + "=" * 80)
        print("COMPREHENSIVE ANALYSIS REPORT")
        print("=" * 80)
        
        # Metadata
        metadata = analysis.get("metadata", {})
        print(f"\nStrategy: {metadata.get('strategy_name', 'Unknown')}")
        print(f"Test Suite: {metadata.get('test_suite_name', 'Unknown')}")
        print(f"Total Results: {metadata.get('total_results', 0)}")
        
        # Accuracy Analysis
        print("\n" + "-" * 40)
        print("ACCURACY ANALYSIS")
        print("-" * 40)
        
        accuracy = analysis.get("accuracy", {})
        print(f"Success Rate: {accuracy.get('success_rate', 0):.1f}% ({accuracy.get('successful_tests', 0)}/{accuracy.get('total_tests', 0)})")
        
        # Latency Analysis
        print("\n" + "-" * 40)
        print("LATENCY ANALYSIS")
        print("-" * 40)
        
        latency = analysis.get("latency", {})
        if "error" not in latency:
            print(f"Average Latency: {latency.get('average_ms', 0):.2f}ms")
            print(f"Median Latency: {latency.get('median_ms', 0):.2f}ms")
            print(f"Min/Max: {latency.get('min_ms', 0):.2f}ms / {latency.get('max_ms', 0):.2f}ms")
            
            percentiles = latency.get("percentiles", {})
            print(f"Percentiles - P90: {percentiles.get('p90', 0):.2f}ms, P95: {percentiles.get('p95', 0):.2f}ms, P99: {percentiles.get('p99', 0):.2f}ms")
            
            print("\nLatency Distribution:")
            distribution = latency.get("distribution", {})
            for bucket, count in distribution.items():
                percentage = (count / latency.get('total_measurements', 1)) * 100
                print(f"  {bucket.replace('_', ' ')}: {count} ({percentage:.1f}%)")
        
        # Tool Usage Analysis
        print("\n" + "-" * 40)
        print("TOOL USAGE ANALYSIS")
        print("-" * 40)
        
        tool_usage = analysis.get("tool_usage", {})
        print(f"Unique Tools Used: {tool_usage.get('unique_tools', 0)}")
        
        tool_breakdown = tool_usage.get("tool_breakdown", {})
        if tool_breakdown:
            print("\nTool Performance:")
            for tool_name, stats in sorted(tool_breakdown.items(), key=lambda x: x[1]["times_expected"], reverse=True):
                print(f"  {tool_name:20} - Used: {stats['times_expected']:3}x, Success: {stats['success_rate']:5.1f}%, Accuracy: {stats['accuracy']:5.1f}%")
        
        # Failure Analysis
        print("\n" + "-" * 40)
        print("FAILURE ANALYSIS")
        print("-" * 40)
        
        failures = analysis.get("failure_analysis", {})
        print(f"Total Failures: {failures.get('total_failures', 0)} ({failures.get('failure_rate', 0):.1f}%)")
        
        if failures.get("total_failures", 0) > 0:
            print("\nFailure Categories:")
            categories = failures.get("failure_categories", {})
            for category, count in categories.items():
                if count > 0:
                    print(f"  {category.replace('_', ' ').title()}: {count}")
        
        # Scenario Breakdown
        print("\n" + "-" * 40)
        print("SCENARIO BREAKDOWN")
        print("-" * 40)
        
        scenarios = analysis.get("scenario_breakdown", {})
        if scenarios:
            print(f"{'Scenario':<30} {'Success Rate':<12} {'Avg Latency':<12} {'Attempts':<10}")
            print("-" * 64)
            for scenario_name, stats in sorted(scenarios.items(), key=lambda x: x[1]["success_rate"], reverse=True):
                print(f"{scenario_name[:29]:<30} {stats['success_rate']:>6.1f}%     {stats['average_latency_ms']:>8.2f}ms   {stats['attempts']:>8}")
        
        print("\n" + "=" * 80) 