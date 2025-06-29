import os
import time
import json
from openai import OpenAI
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
import argparse

# Initialize the OpenAI client using the API key from environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

@dataclass
class TestResult:
    """Represents the result of a single test"""
    scenario_name: str
    success: bool
    latency_ms: float
    actual_tool_calls: Optional[List[Dict[str, Any]]]
    expected_tool_calls: List[Dict[str, Any]]
    validation_details: Dict[str, Any]
    error: Optional[str] = None
    model_response: Optional[str] = None
    tokens_used: Optional[Dict[str, int]] = None

class ToolCallAccuracyTester:
    """Main class for testing tool call accuracy"""
    
    def __init__(self, model: str = "o3", verbose: bool = True):
        self.model = model
        self.verbose = verbose
        self.results: List[TestResult] = []
        
    def run_test(self, scenario: TestScenario) -> TestResult:
        """Run a single test scenario"""
        if self.verbose:
            print(f"\nRunning test: {scenario.name}")
            print(f"Prompt: {scenario.prompt}")
        
        start_time = time.time()
        
        try:
            # Make the API call
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Use the provided tools when appropriate to answer user queries. Be precise in your tool usage."
                    },
                    {
                        "role": "user",
                        "content": scenario.prompt
                    }
                ],
                tools=[tool.to_dict() for tool in scenario.tools],
                tool_choice="auto"
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Extract tool calls
            actual_tool_calls = []
            if response.choices[0].message.tool_calls:
                for tc in response.choices[0].message.tool_calls:
                    actual_tool_calls.append({
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments) if tc.function.arguments else {}
                    })
            
            # Validate the results
            validation_details = self.validate_tool_calls(
                actual_tool_calls, 
                scenario.expected_tool_calls,
                scenario.validation_function
            )
            
            success = validation_details.get("matches_expected", False)
            
            result = TestResult(
                scenario_name=scenario.name,
                success=success,
                latency_ms=round(latency_ms, 2),
                actual_tool_calls=actual_tool_calls,
                expected_tool_calls=scenario.expected_tool_calls,
                validation_details=validation_details,
                model_response=response.choices[0].message.content,
                tokens_used={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
            
        except Exception as e:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            result = TestResult(
                scenario_name=scenario.name,
                success=False,
                latency_ms=round(latency_ms, 2),
                actual_tool_calls=None,
                expected_tool_calls=scenario.expected_tool_calls,
                validation_details={"error": str(e)},
                error=str(e)
            )
        
        self.results.append(result)
        
        if self.verbose:
            self.print_result(result)
        
        return result
    
    def validate_tool_calls(self, actual: List[Dict], expected: List[Dict], 
                           custom_validator: Optional[Callable] = None) -> Dict[str, Any]:
        """Validate actual tool calls against expected ones"""
        validation_details = {
            "matches_expected": False,
            "correct_tool_count": len(actual) == len(expected),
            "actual_count": len(actual),
            "expected_count": len(expected),
            "tool_name_matches": [],
            "argument_matches": [],
            "missing_tools": [],
            "extra_tools": []
        }
        
        # Custom validation function takes precedence
        if custom_validator:
            custom_result = custom_validator(actual, expected)
            validation_details.update(custom_result)
            return validation_details
        
        # Default validation logic
        if not validation_details["correct_tool_count"]:
            validation_details["matches_expected"] = False
            return validation_details
        
        # Check each expected tool call
        matched_indices = set()
        for exp in expected:
            found = False
            for i, act in enumerate(actual):
                if i in matched_indices:
                    continue
                    
                if act["name"] == exp["name"]:
                    validation_details["tool_name_matches"].append(exp["name"])
                    
                    # Check arguments
                    args_match = self.compare_arguments(act.get("arguments", {}), 
                                                       exp.get("arguments", {}))
                    if args_match:
                        validation_details["argument_matches"].append({
                            "tool": exp["name"],
                            "matches": True
                        })
                        matched_indices.add(i)
                        found = True
                        break
                    else:
                        validation_details["argument_matches"].append({
                            "tool": exp["name"],
                            "matches": False,
                            "expected": exp.get("arguments", {}),
                            "actual": act.get("arguments", {})
                        })
            
            if not found:
                validation_details["missing_tools"].append(exp)
        
        # Check for extra tools
        for i, act in enumerate(actual):
            if i not in matched_indices:
                validation_details["extra_tools"].append(act)
        
        # Overall success
        validation_details["matches_expected"] = (
            len(validation_details["missing_tools"]) == 0 and
            len(validation_details["extra_tools"]) == 0 and
            all(match["matches"] for match in validation_details["argument_matches"])
        )
        
        return validation_details
    
    def compare_arguments(self, actual: Dict, expected: Dict) -> bool:
        """Compare tool arguments, allowing for some flexibility"""
        # For now, do exact match. Can be extended for fuzzy matching
        return actual == expected
    
    def print_result(self, result: TestResult):
        """Print a single test result"""
        status = "✓ PASS" if result.success else "✗ FAIL"
        print(f"{status} - Latency: {result.latency_ms}ms")
        
        if result.actual_tool_calls:
            print(f"  Tool calls made: {len(result.actual_tool_calls)}")
            for tc in result.actual_tool_calls:
                print(f"    - {tc['name']}({json.dumps(tc['arguments'])})")
        else:
            print("  No tool calls made")
        
        if not result.success:
            print(f"  Validation: {result.validation_details}")
        
        if result.error:
            print(f"  Error: {result.error}")
    
    def run_test_suite(self, scenarios: List[TestScenario], 
                      tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run multiple test scenarios"""
        print("=" * 60)
        print(f"Tool Call Accuracy Test Suite")
        print(f"Model: {self.model}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Filter scenarios by tags if specified
        if tags:
            scenarios = [s for s in scenarios if any(tag in s.tags for tag in tags)]
        
        # Run all tests
        for scenario in scenarios:
            self.run_test(scenario)
            time.sleep(0.5)  # Small delay between tests
        
        # Generate summary
        summary = self.generate_summary()
        
        return summary
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary statistics"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        
        latencies = [r.latency_ms for r in self.results]
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "average_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "min_latency_ms": min(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0,
            "tests_by_scenario": {}
        }
        
        # Group results by scenario
        for result in self.results:
            summary["tests_by_scenario"][result.scenario_name] = {
                "success": result.success,
                "latency_ms": result.latency_ms,
                "validation_details": result.validation_details
            }
        
        return summary
    
    def save_results(self, filename: Optional[str] = None):
        """Save test results to JSON file"""
        if not filename:
            filename = f"tool_accuracy_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "summary": self.generate_summary(),
            "detailed_results": [asdict(r) for r in self.results]
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
        return filename

# Load test scenarios from configuration file
def load_test_scenarios(config_file: str = "test_scenarios.json") -> List[TestScenario]:
    """Load test scenarios from a JSON configuration file"""
    if not os.path.exists(config_file):
        return get_default_test_scenarios()
    
    with open(config_file, 'r') as f:
        data = json.load(f)
    
    scenarios = []
    for scenario_data in data.get("scenarios", []):
        tools = [
            ToolDefinition(
                name=t["name"],
                description=t["description"],
                parameters=t["parameters"]
            )
            for t in scenario_data.get("tools", [])
        ]
        
        scenario = TestScenario(
            name=scenario_data["name"],
            description=scenario_data.get("description", ""),
            prompt=scenario_data["prompt"],
            tools=tools,
            expected_tool_calls=scenario_data.get("expected_tool_calls", []),
            tags=scenario_data.get("tags", [])
        )
        scenarios.append(scenario)
    
    return scenarios

# Default test scenarios
def get_default_test_scenarios() -> List[TestScenario]:
    """Get default test scenarios"""
    
    # Define reusable tools
    weather_tool = ToolDefinition(
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
                    "description": "The temperature unit"
                }
            },
            "required": ["location"]
        }
    )
    
    calculator_tool = ToolDefinition(
        name="calculate",
        description="Perform mathematical calculations",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    )
    
    search_tool = ToolDefinition(
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
    
    # Define test scenarios
    scenarios = [
        TestScenario(
            name="Simple Weather Query",
            description="Test basic weather tool usage",
            prompt="What's the weather in San Francisco?",
            tools=[weather_tool],
            expected_tool_calls=[
                {"name": "get_weather", "arguments": {"location": "San Francisco, CA"}}
            ],
            tags=["weather", "simple"]
        ),
        
        TestScenario(
            name="Weather with Unit",
            description="Test weather tool with temperature unit",
            prompt="What's the weather in New York in celsius?",
            tools=[weather_tool],
            expected_tool_calls=[
                {"name": "get_weather", "arguments": {"location": "New York, NY", "unit": "celsius"}}
            ],
            tags=["weather", "parameters"]
        ),
        
        TestScenario(
            name="Simple Math",
            description="Test basic calculation",
            prompt="What is 15 * 23?",
            tools=[calculator_tool],
            expected_tool_calls=[
                {"name": "calculate", "arguments": {"expression": "15 * 23"}}
            ],
            tags=["math", "simple"]
        ),
        
        TestScenario(
            name="Complex Math",
            description="Test complex mathematical expression",
            prompt="Calculate the square root of 144 plus 10% of 200",
            tools=[calculator_tool],
            expected_tool_calls=[
                {"name": "calculate", "arguments": {"expression": "sqrt(144) + 0.1 * 200"}}
            ],
            tags=["math", "complex"]
        ),
        
        TestScenario(
            name="Multiple Tool Calls",
            description="Test multiple tool calls in one request",
            prompt="What's the weather in both San Francisco and New York?",
            tools=[weather_tool],
            expected_tool_calls=[
                {"name": "get_weather", "arguments": {"location": "San Francisco, CA"}},
                {"name": "get_weather", "arguments": {"location": "New York, NY"}}
            ],
            tags=["weather", "multiple"]
        ),
        
        TestScenario(
            name="Mixed Tools",
            description="Test using different tools in one request",
            prompt="What's the weather in London and what's 50 divided by 7?",
            tools=[weather_tool, calculator_tool],
            expected_tool_calls=[
                {"name": "get_weather", "arguments": {"location": "London, UK"}},
                {"name": "calculate", "arguments": {"expression": "50 / 7"}}
            ],
            tags=["mixed", "multiple"]
        ),
        
        TestScenario(
            name="No Tool Needed",
            description="Test when no tool should be called",
            prompt="Tell me a joke about programmers",
            tools=[weather_tool, calculator_tool],
            expected_tool_calls=[],
            tags=["no-tool"]
        ),
        
        TestScenario(
            name="Ambiguous Request",
            description="Test tool selection with ambiguous request",
            prompt="I need information about Paris",
            tools=[weather_tool, search_tool],
            expected_tool_calls=[
                {"name": "search_web", "arguments": {"query": "Paris information"}}
            ],
            tags=["ambiguous", "selection"]
        ),
        
        TestScenario(
            name="Search with Parameters",
            description="Test search tool with optional parameters",
            prompt="Search for the latest news about AI, show me 10 results",
            tools=[search_tool],
            expected_tool_calls=[
                {"name": "search_web", "arguments": {"query": "latest news about AI", "num_results": 10}}
            ],
            tags=["search", "parameters"]
        )
    ]
    
    return scenarios

def main():
    """Main function to run the tool call accuracy tests"""
    parser = argparse.ArgumentParser(description="Test OpenAI model tool call accuracy")
    parser.add_argument("--model", default="o3", help="Model to test (default: o3)")
    parser.add_argument("--config", default="test_scenarios.json", help="Test scenarios config file")
    parser.add_argument("--tags", nargs="+", help="Filter scenarios by tags")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output", help="Output filename for results")
    
    args = parser.parse_args()
    
    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    # Load test scenarios
    scenarios = load_test_scenarios(args.config)
    
    # Create tester instance
    tester = ToolCallAccuracyTester(model=args.model, verbose=args.verbose)
    
    # Run tests
    summary = tester.run_test_suite(scenarios, tags=args.tags)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    print(f"Average latency: {summary['average_latency_ms']:.2f}ms")
    
    # Save results
    tester.save_results(args.output)

if __name__ == "__main__":
    main() 