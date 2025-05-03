# Bedrock Agent Tester

This repository contains testing frameworks for AWS Bedrock Agents, specifically for:
- ClinicalTrials.gov API Agent
- OpenFDA API Agent

## Project Structure

```
bedrock-agent-tester/
├── clinical-tester/         # ClinicalTrials.gov API testing framework
│   ├── README.md
│   ├── test_cases.json
│   └── test_runner.py
├── openfda-tester/          # OpenFDA API testing framework
│   ├── README.md
│   ├── test_cases.json
│   └── test_runner.py
├── config/                  # Agent configurations
│   └── agents.json         # Configuration for all agents
└── README.md               # This file
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bedrock-agent-tester.git
   cd bedrock-agent-tester
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

4. Configure your agents:
   - Copy `config/agents.json.example` to `config/agents.json`
   - Update the configuration with your agent IDs and alias IDs

## Usage

### Clinical Trials Agent Testing
```bash
cd clinical-tester
python test_runner.py
```

### OpenFDA Agent Testing
```bash
cd openfda-tester
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