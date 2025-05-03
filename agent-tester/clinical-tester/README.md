# Clinical Trials Agent Tester

This directory contains test cases and utilities for testing the ClinicalTrials.gov API agent.

## Structure

- `test_cases.json`: Contains categorized test cases for different aspects of the agent
- `test_runner.py`: Script to execute test cases and validate responses
- `results/`: Directory to store test results and logs

## Configuration

The agent configuration is stored in the root `config/agents.json` file. This file contains configurations for all agents, with the clinical trials agent configuration under the `clinical_trials` key.

Example configuration:
```json
{
    "clinical_trials": {
        "agent_id": "YOUR_AGENT_ID",
        "agent_alias_id": "YOUR_AGENT_ALIAS_ID",
        "region": "us-east-1",
        "name": "Clinical Trials Agent",
        "description": "Agent for querying ClinicalTrials.gov API",
        "version": "1.0.0"
    }
}
```

## Test Categories

1. Basic Trial Information
2. Specific Trial Details
3. Location and Site-based
4. Demographic and Population
5. Treatment and Intervention
6. Status and Timeline
7. Complex Combination
8. Safety and Adverse Events
9. Sponsor and Funding
10. Results and Outcomes

## Usage

1. Configure your agent connection details in `config/agents.json`
2. Run tests using: `python test_runner.py`
3. Review results in the `results/` directory

## Adding New Test Cases

Add new test cases to `test_cases.json` following the existing structure:

```json
{
  "category": "Test Category",
  "test_cases": [
    {
      "id": "unique_id",
      "question": "Test question",
      "expected_elements": ["expected", "response", "elements"]
    }
  ]
}
``` 