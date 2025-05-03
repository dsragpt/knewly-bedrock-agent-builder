import json
import os
from datetime import datetime
import boto3
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OpenFDATester:
    def __init__(self, config_path='../../config/agents.json'):
        self.config = self._load_config(config_path)
        self.bedrock_client = self._setup_bedrock_client()
        self.test_cases = self._load_test_cases()
        
    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config['openfda']  # Get the OpenFDA agent config
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file {config_path}")
            raise
        except KeyError:
            logger.error("OpenFDA agent configuration not found in config file")
            raise

    def _setup_bedrock_client(self):
        """Set up AWS Bedrock client"""
        try:
            return boto3.client(
                'bedrock-agent-runtime',
                region_name=self.config.get('region', 'us-east-1')
            )
        except Exception as e:
            logger.error(f"Failed to set up Bedrock client: {str(e)}")
            raise

    def _load_test_cases(self):
        """Load test cases from JSON file"""
        try:
            with open('test_cases.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Test cases file not found")
            raise
        except json.JSONDecodeError:
            logger.error("Invalid JSON in test cases file")
            raise

    def run_test_case(self, test_case):
        """Run a single test case"""
        try:
            response = self.bedrock_client.invoke_agent(
                agentId=self.config['agent_id'],
                agentAliasId=self.config['agent_alias_id'],
                sessionId=f"test-session-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                inputText=test_case['question']
            )
            
            # Process and validate response
            return {
                'test_id': test_case['id'],
                'question': test_case['question'],
                'response': response,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error running test case {test_case['id']}: {str(e)}")
            return {
                'test_id': test_case['id'],
                'question': test_case['question'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def run_all_tests(self):
        """Run all test cases"""
        results = []
        for category in self.test_cases['categories']:
            logger.info(f"Running tests for category: {category['name']}")
            for test_case in category['test_cases']:
                result = self.run_test_case(test_case)
                results.append(result)
        
        # Save results
        self._save_results(results)
        return results

    def _save_results(self, results):
        """Save test results to file"""
        os.makedirs('results', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'results/test_results_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {filename}")

if __name__ == "__main__":
    tester = OpenFDATester()
    tester.run_all_tests() 