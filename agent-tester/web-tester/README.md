# Web Search Tester

This directory contains test cases and a test runner for testing the web search functionality of the agent, including both SERP (Google Search) and Tavily search implementations.

## Features Tested

- Basic search functionality for both SERP and Tavily
- Search with metadata (URLs, titles, relevance scores)
- Consolidated results with summaries
- Targeted website search
- Complex search queries

## Setup

1. Ensure you have the required environment variables set:
   ```bash
   export AGENT_ID="your-agent-id"
   export AGENT_ALIAS_ID="your-agent-alias-id"
   ```

2. Install the required dependencies:
   ```bash
   pip install boto3
   ```

## Running Tests

To run the tests:

```bash
python test_runner.py
```

The test runner will:
1. Load test cases from `test_cases.json`
2. Execute each test case
3. Print a summary of the results
4. Save detailed results to `test_results.json`

## Test Cases

The test cases in `test_cases.json` cover various aspects of web search functionality:

- Basic search queries
- Search with metadata requests
- Search with consolidated results
- Targeted website searches
- Complex queries with multiple parameters

## Test Results

The test results include:
- Test case name and description
- Input provided
- Response received
- Success/failure status
- Duration of the test
- Any errors encountered

## Customizing Tests

To add new test cases:
1. Edit `test_cases.json`
2. Add a new test case object with:
   - `name`: Test case name
   - `input`: The search query to test
   - `description`: Description of what the test verifies

## Notes

- The test runner checks for the presence of search-related actions in the response
- Success is determined by whether the agent attempted to perform a search
- The actual content of search results may vary between runs 