"""
Shared validation utilities
"""

from typing import Dict, List, Any, Optional, Callable
import json


def validate_tool_calls(actual: List[Dict], expected: List[Dict], 
                       custom_validator: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Validate actual tool calls against expected ones
    
    Args:
        actual: List of actual tool calls made by the model
        expected: List of expected tool calls
        custom_validator: Optional custom validation function
    
    Returns:
        Dict containing validation results and details
    """
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
        try:
            custom_result = custom_validator(actual, expected)
            validation_details.update(custom_result)
            return validation_details
        except Exception as e:
            validation_details["error"] = f"Custom validator failed: {str(e)}"
            return validation_details
    
    # Default validation logic
    if not validation_details["correct_tool_count"]:
        validation_details["matches_expected"] = False
        validation_details["reason"] = f"Expected {len(expected)} tool calls, got {len(actual)}"
        return validation_details
    
    # Check each expected tool call
    matched_indices = set()
    for exp in expected:
        found = False
        for i, act in enumerate(actual):
            if i in matched_indices:
                continue
                
            if act.get("name") == exp.get("name"):
                validation_details["tool_name_matches"].append(exp.get("name"))
                
                # Check arguments
                args_match = compare_arguments(act.get("arguments", {}), 
                                               exp.get("arguments", {}))
                if args_match:
                    validation_details["argument_matches"].append({
                        "tool": exp.get("name"),
                        "matches": True
                    })
                    matched_indices.add(i)
                    found = True
                    break
                else:
                    validation_details["argument_matches"].append({
                        "tool": exp.get("name"),
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
        all(match.get("matches", False) for match in validation_details["argument_matches"])
    )
    
    # Add reason for failure
    if not validation_details["matches_expected"]:
        reasons = []
        if validation_details["missing_tools"]:
            reasons.append(f"Missing tools: {[t.get('name') for t in validation_details['missing_tools']]}")
        if validation_details["extra_tools"]:
            reasons.append(f"Extra tools: {[t.get('name') for t in validation_details['extra_tools']]}")
        if any(not match.get("matches", False) for match in validation_details["argument_matches"]):
            reasons.append("Argument mismatches")
        validation_details["reason"] = "; ".join(reasons)
    
    return validation_details


def compare_arguments(actual: Dict, expected: Dict, fuzzy: bool = False) -> bool:
    """
    Compare tool arguments, with optional fuzzy matching
    
    Args:
        actual: Actual arguments from model
        expected: Expected arguments
        fuzzy: Whether to do fuzzy/flexible matching
    
    Returns:
        True if arguments match, False otherwise
    """
    if not fuzzy:
        return actual == expected
    
    # Fuzzy matching logic - can be extended as needed
    if len(actual) != len(expected):
        return False
    
    for key, exp_value in expected.items():
        if key not in actual:
            return False
        
        act_value = actual[key]
        
        # For strings, do case-insensitive comparison and handle common variations
        if isinstance(exp_value, str) and isinstance(act_value, str):
            exp_clean = exp_value.lower().strip().replace(",", "").replace(".", "")
            act_clean = act_value.lower().strip().replace(",", "").replace(".", "")
            
            if exp_clean != act_clean:
                # Check if actual contains all words from expected
                exp_words = set(exp_clean.split())
                act_words = set(act_clean.split())
                if not exp_words.issubset(act_words):
                    return False
        
        # For numbers, allow small floating point differences
        elif isinstance(exp_value, (int, float)) and isinstance(act_value, (int, float)):
            if abs(exp_value - act_value) > 1e-6:
                return False
        
        # For other types, require exact match
        elif exp_value != act_value:
            return False
    
    return True


def flexible_location_validator(actual: List[Dict], expected: List[Dict]) -> Dict[str, Any]:
    """
    Example custom validator that's more flexible with location formatting
    """
    if len(actual) != len(expected):
        return {"matches_expected": False, "reason": "Different number of tool calls"}
    
    for i, (act, exp) in enumerate(zip(actual, expected)):
        if act.get("name") != exp.get("name"):
            return {"matches_expected": False, "reason": f"Tool name mismatch at index {i}"}
        
        # More flexible location matching
        act_location = act.get("arguments", {}).get("location", "").lower()
        exp_location = exp.get("arguments", {}).get("location", "").lower()
        
        # Remove common variations
        act_location = act_location.replace(",", "").replace(".", "")
        exp_location = exp_location.replace(",", "").replace(".", "")
        
        # Check if the key parts match
        if not all(part in act_location for part in exp_location.split()):
            return {
                "matches_expected": False,
                "reason": f"Location mismatch: expected '{exp_location}', got '{act_location}'"
            }
    
    return {"matches_expected": True} 