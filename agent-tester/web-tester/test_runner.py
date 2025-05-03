import json
import os
import sys
import boto3
import time
from typing import Dict, Any, List

# Add parent directory to path to import test_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_utils import (
    invoke_agent,
    parse_response,
    format_test_result,
    print_test_summary,
    save_test_results
)

def run_web_search_test(
    test_case: Dict[str, Any],
    agent_id: str,
    agent_alias_id: str,
    bedrock_client: Any
) -> Dict[str, Any]:
    """Run a single web search test case."""
    start_time = time.time()
    
    try:
        # Prepare the input
        input_text = test_case["input"]
        
        # Invoke the agent
        response = invoke_agent(
            agent_id=agent_id,
            agent_alias_id=agent_alias_id,
            input_text=input_text,
            bedrock_client=bedrock_client
        )
        
        # Parse the response
        parsed_response = parse_response(response)
        
        # Check if the response contains search results
        has_search_results = any(
            "search" in action.lower() or "tavily" in action.lower()
            for action in parsed_response.get("actions", [])
        )
        
        # Calculate test duration
        duration = time.time() - start_time
        
        # Format the test result
        return format_test_result(
            test_case=test_case,
            parsed_response=parsed_response,
            duration=duration,
            success=has_search_results
        )
        
    except Exception as e:
        duration = time.time() - start_time
        return format_test_result(
            test_case=test_case,
            error=str(e),
            duration=duration,
            success=False
        )

def main():
    # Load test cases
    with open("test_cases.json", "r") as f:
        test_cases = json.load(f)
    
    # Initialize Bedrock client
    bedrock_client = boto3.client("bedrock-agent-runtime")
    
    # Get agent IDs from environment variables
    agent_id = os.getenv("AGENT_ID")
    agent_alias_id = os.getenv("AGENT_ALIAS_ID")
    
    if not agent_id or not agent_alias_id:
        print("Error: AGENT_ID and AGENT_ALIAS_ID environment variables must be set")
        sys.exit(1)
    
    # Run tests
    results = []
    for test_case in test_cases:
        result = run_web_search_test(
            test_case=test_case,
            agent_id=agent_id,
            agent_alias_id=agent_alias_id,
            bedrock_client=bedrock_client
        )
        results.append(result)
    
    # Print summary
    print_test_summary(results)
    
    # Save results
    save_test_results(results, "test_results.json")

if __name__ == "__main__":
    main() 