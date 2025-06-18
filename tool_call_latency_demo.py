import os
import time
import json
from openai import OpenAI
from typing import Dict, List, Any
from datetime import datetime

# Initialize the OpenAI client using the API key from environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Define a simple tool for the model to call
def get_weather_tool():
    """Returns the tool definition for getting weather information"""
    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
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
        }
    }

def calculate_math_tool():
    """Returns the tool definition for calculating math expressions"""
    return {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform a mathematical calculation",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate, e.g. '2 + 2' or 'sqrt(16)'"
                    }
                },
                "required": ["expression"]
            }
        }
    }

def measure_tool_call_latency(prompt: str, tools: List[Dict[str, Any]], model: str = "o3") -> Dict[str, Any]:
    """
    Measures the time it takes for the model to return a tool call
    
    Args:
        prompt: The user prompt that should trigger a tool call
        tools: List of tool definitions
        model: The model to use (default: o3)
    
    Returns:
        Dictionary containing timing information and the response
    """
    
    # Record start time
    start_time = time.time()
    
    try:
        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use the provided tools when appropriate to answer user queries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            tools=tools,
            tool_choice="auto"  # Let the model decide when to use tools
        )
        
        # Record end time
        end_time = time.time()
        
        # Calculate latency
        latency_ms = (end_time - start_time) * 1000
        
        # Extract tool call information if present
        tool_calls = None
        if response.choices[0].message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in response.choices[0].message.tool_calls
            ]
        
        return {
            "success": True,
            "latency_ms": round(latency_ms, 2),
            "model": model,
            "prompt": prompt,
            "tool_calls": tool_calls,
            "message": response.choices[0].message.content,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        
    except Exception as e:
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        return {
            "success": False,
            "latency_ms": round(latency_ms, 2),
            "model": model,
            "prompt": prompt,
            "error": str(e)
        }

def run_latency_tests():
    """Run multiple test scenarios and measure latencies"""
    
    print("=" * 60)
    print("OpenAI Tool Call Latency Measurement Demo")
    print(f"Using model: o3")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    print()
    
    # Define test scenarios
    test_scenarios = [
        {
            "name": "Weather Query",
            "prompt": "What's the weather like in San Francisco?",
            "tools": [get_weather_tool()]
        },
        {
            "name": "Math Calculation",
            "prompt": "Calculate the square root of 144",
            "tools": [calculate_math_tool()]
        },
        {
            "name": "Multiple Tools Available",
            "prompt": "What's the weather in New York and what's 15 * 23?",
            "tools": [get_weather_tool(), calculate_math_tool()]
        },
        {
            "name": "No Tool Needed",
            "prompt": "Tell me a joke about programmers",
            "tools": [get_weather_tool(), calculate_math_tool()]
        }
    ]
    
    results = []
    
    for scenario in test_scenarios:
        print(f"Test: {scenario['name']}")
        print(f"Prompt: {scenario['prompt']}")
        print("Running...", end="", flush=True)
        
        result = measure_tool_call_latency(
            prompt=scenario['prompt'],
            tools=scenario['tools']
        )
        
        results.append({
            "scenario": scenario['name'],
            **result
        })
        
        print(f" Done! Latency: {result['latency_ms']}ms")
        
        if result['success']:
            if result['tool_calls']:
                print(f"Tool calls made: {len(result['tool_calls'])}")
                for tc in result['tool_calls']:
                    print(f"  - {tc['function']['name']}({tc['function']['arguments']})")
            else:
                print("No tool calls made (direct response)")
            
            print(f"Tokens used: {result['usage']['total_tokens']}")
        else:
            print(f"Error: {result['error']}")
        
        print("-" * 40)
        print()
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    
    successful_results = [r for r in results if r['success']]
    
    if successful_results:
        latencies = [r['latency_ms'] for r in successful_results]
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        print(f"Total tests run: {len(results)}")
        print(f"Successful tests: {len(successful_results)}")
        print(f"Average latency: {avg_latency:.2f}ms")
        print(f"Min latency: {min_latency}ms")
        print(f"Max latency: {max_latency}ms")
        
        print("\nLatency by scenario:")
        for result in successful_results:
            tool_info = "with tool call" if result['tool_calls'] else "no tool call"
            print(f"  {result['scenario']}: {result['latency_ms']}ms ({tool_info})")
    
    # Save results to file
    output_filename = f"tool_call_latency_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_filename, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "model": "o3",
            "results": results,
            "summary": {
                "total_tests": len(results),
                "successful_tests": len(successful_results),
                "average_latency_ms": avg_latency if successful_results else 0,
                "min_latency_ms": min_latency if successful_results else 0,
                "max_latency_ms": max_latency if successful_results else 0
            }
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_filename}")

if __name__ == "__main__":
    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    # Run the latency tests
    run_latency_tests() 