"""
OpenAI reasoning strategy implementation
"""

import os
import time
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI

from .base_strategy import BaseReasoningStrategy
from tool_params.tool_definitions import TestScenario, ExecutionResult


class OpenAIStrategy(BaseReasoningStrategy):
    """
    Reasoning strategy that uses OpenAI's API for tool calling
    """
    
    def __init__(self, model: str = "o3", api_key: Optional[str] = None, 
                 verbose: bool = False, **kwargs):
        super().__init__(name=f"OpenAI-{model}", verbose=verbose)
        
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Additional configuration
        self.system_prompt = kwargs.get("system_prompt", 
            "You are a helpful assistant. Use the provided tools when appropriate to answer user queries. Be precise in your tool usage.")
        self.temperature = kwargs.get("temperature", 0.1)
        self.max_tokens = kwargs.get("max_tokens", None)
        self.timeout = kwargs.get("timeout", 30)
    
    def execute_scenario(self, scenario: TestScenario) -> ExecutionResult:
        """Execute a test scenario using OpenAI's API"""
        
        if self.verbose:
            print(f"  Executing with model: {self.model}")
        
        # Record start time
        start_time = time.time()
        
        try:
            # Prepare tools for OpenAI API
            tools = [tool.to_dict() for tool in scenario.tools]
            
            # Make the API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": scenario.prompt
                    }
                ],
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
            
            # Record end time
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Extract tool calls
            actual_tool_calls = []
            if response.choices[0].message.tool_calls:
                for tc in response.choices[0].message.tool_calls:
                    try:
                        arguments = json.loads(tc.function.arguments) if tc.function.arguments else {}
                    except json.JSONDecodeError:
                        arguments = {"_raw": tc.function.arguments}
                    
                    actual_tool_calls.append({
                        "name": tc.function.name,
                        "arguments": arguments
                    })
            
            # Extract token usage
            tokens_used = None
            if response.usage:
                tokens_used = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            return ExecutionResult(
                success=True,
                latency_ms=round(latency_ms, 2),
                actual_tool_calls=actual_tool_calls,
                model_response=response.choices[0].message.content,
                tokens_used=tokens_used,
                metadata={
                    "model": self.model,
                    "finish_reason": response.choices[0].finish_reason,
                    "system_prompt": self.system_prompt
                }
            )
            
        except Exception as e:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            if self.verbose:
                print(f"  Error executing scenario: {str(e)}")
            
            return ExecutionResult(
                success=False,
                latency_ms=round(latency_ms, 2),
                actual_tool_calls=None,
                error=str(e),
                metadata={
                    "model": self.model,
                    "system_prompt": self.system_prompt
                }
            )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return information about this strategy's capabilities"""
        return {
            "name": self.name,
            "provider": "OpenAI",
            "model": self.model,
            "supports_tool_calls": True,
            "supports_streaming": False,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system_prompt": self.system_prompt
        }
    
    def validate_scenario(self, scenario: TestScenario) -> bool:
        """Check if this strategy can handle the given scenario"""
        # OpenAI supports tool calling, so we can handle any scenario with tools
        # Could add more sophisticated validation here if needed
        return True
    
    def set_model(self, model: str):
        """Change the model used by this strategy"""
        self.model = model
        self.name = f"OpenAI-{model}"
    
    def set_system_prompt(self, prompt: str):
        """Change the system prompt used by this strategy"""
        self.system_prompt = prompt
    
    def set_temperature(self, temperature: float):
        """Change the temperature used by this strategy"""
        self.temperature = temperature 