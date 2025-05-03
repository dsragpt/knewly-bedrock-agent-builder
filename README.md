# Knewly Bedrock Agent Builder

This repository contains testing frameworks for AWS Bedrock Agents, specifically for:
- ClinicalTrials.gov API Agent
- OpenFDA API Agent

## Project Structure

```
knewly-bedrock-agent-builder/
├── action/                 # Bedrock Agent Action Groups
│   ├── clinical/          # ClinicalTrials.gov API actions
│   │   ├── lambda.py      # Lambda function for ClinicalTrials.gov API
│   │   └── schema.json    # Action schema for ClinicalTrials.gov API
│   ├── openfda/           # OpenFDA API actions
│   │   ├── lambda.py      # Lambda function for OpenFDA API
│   │   └── schema.json    # Action schema for OpenFDA API
│   └── web/               # Web-related actions
│       ├── lambda.py      # Lambda function for web actions
│       └── schema.json    # Action schema for web actions
├── action-examples/       # Working reference implementations
│   ├── clinical/         # Reference ClinicalTrials.gov implementation
│   │   ├── dummy_lambda.py
│   │   └── schema.json
│   ├── openfda/          # Reference OpenFDA implementation
│   │   ├── dummy_lambda.py
│   │   └── schema.json
│   └── web/              # Reference web search implementation
│       ├── dummy_lambda.py
│       ├── action_serp.json
│       └── action_tavily.json
├── agent-tester/          # Testing frameworks
│   ├── clinical-tester/   # ClinicalTrials.gov API testing framework
│   │   ├── README.md
│   │   ├── test_cases.json
│   │   └── test_runner.py
│   └── openfda-tester/    # OpenFDA API testing framework
│       ├── README.md
│       ├── test_cases.json
│       └── test_runner.py
├── config/                # Agent configurations
│   └── agents.json       # Configuration for all agents
└── README.md             # This file
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/knewly-bedrock-agent-builder.git
   cd knewly-bedrock-agent-builder
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Lambda Layer Dependencies:
   - The clinical actions require the `requests` library as a Lambda layer
   - The layer is available at `agent-builder/action/clinical/requests-layer.zip`
   - When deploying the clinical Lambda function, add this as a layer

5. Configure your agents:
   - Copy `config/agents.json.example` to `config/agents.json`
   - Update the configuration with your agent IDs and alias IDs

## Usage

### Clinical Trials Agent Testing
```bash
cd agent-tester/clinical-tester
python test_runner.py
```

### OpenFDA Agent Testing
```bash
cd agent-tester/openfda-tester
python test_runner.py
```

## Test Results

Test results are saved in the `results/` directory of each tester with timestamps.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Action Groups

The project includes several action groups for different components of the agent:

1. **ClinicalTrials.gov API Actions** (`action/clinical/`)
   - Lambda function for handling ClinicalTrials.gov API requests
   - Schema defining the available actions and their parameters

2. **OpenFDA API Actions** (`action/openfda/`)
   - Lambda function for handling OpenFDA API requests
   - Schema defining the available actions and their parameters

3. **Web Actions** (`action/web/`)
   - Lambda function for handling web-related operations
   - Schema defining the available web actions and their parameters

Each action group contains:
- `lambda.py`: The Lambda function implementation
- `schema.json`: The action schema defining the available actions, their parameters, and response formats

## Reference Implementations

The `action-examples/` directory contains working reference implementations of all agents:

1. **ClinicalTrials.gov Reference** (`action-examples/clinical/`)
   - Complete working implementation of the ClinicalTrials.gov agent
   - Includes schema and lambda function with all features

2. **OpenFDA Reference** (`action-examples/openfda/`)
   - Complete working implementation of the OpenFDA agent
   - Includes schema and lambda function with all features

3. **Web Search Reference** (`action-examples/web/`)
   - Complete working implementation of web search agents
   - Includes both SERP and Tavily search implementations
   - Features consolidated summaries with source references

These reference implementations serve as:
- Working examples of complete agent implementations
- Templates for creating new agents
- Documentation of best practices and patterns
- Test cases for verifying agent functionality 