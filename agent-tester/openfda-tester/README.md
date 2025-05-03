# OpenFDA API Agent Tester

This directory contains test cases and utilities for testing the OpenFDA API agent, which interacts with both drug and device endpoints.

## Structure

- `test_cases.json`: Contains categorized test cases for different aspects of the agent
- `test_runner.py`: Script to execute test cases and validate responses
- `results/`: Directory to store test results and logs

## Configuration

The agent configuration is stored in the root `config/agents.json` file. This file contains configurations for all agents, with the OpenFDA agent configuration under the `openfda` key.

Example configuration:
```json
{
    "openfda": {
        "agent_id": "YOUR_AGENT_ID",
        "agent_alias_id": "YOUR_AGENT_ALIAS_ID",
        "region": "us-east-1",
        "name": "OpenFDA API Agent",
        "description": "Agent for querying OpenFDA API endpoints",
        "version": "1.0.0"
    }
}
```

## Test Categories

1. Drug Adverse Events
   - Adverse event reports for specific drugs
   - Vaccine adverse events
   - Common adverse events

2. Drug Labeling
   - Warnings and precautions
   - Dosage information
   - Administration instructions

3. Device Recalls
   - Recent recalls
   - Specific device type recalls
   - Recall reasons and affected lots

4. Device Adverse Events
   - Device-specific adverse events
   - Severity and outcomes
   - Patient demographics

5. Combined Drug and Device
   - Interactions between drugs and devices
   - Combined adverse events
   - Related recalls

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