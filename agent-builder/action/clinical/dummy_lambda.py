import json
import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Print requests version to verify it's imported correctly
logger.info(f"Requests library version: {requests.__version__}")

# Constants
BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

def lambda_handler(event, context):
    """AWS Lambda handler for processing Bedrock agent requests."""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        action_group = event['actionGroup']
        api_path = event['apiPath']
        http_method = event['httpMethod']
        parameters = event.get('parameters', [])
        message_version = event.get('messageVersion', '1.0')
        
        # Extract parameters into a dictionary
        param_dict = {param['name']: param['value'] for param in parameters}
        logger.info(f"Extracted parameters: {param_dict}")
        
        # Route to appropriate business logic based on API path
        if api_path == '/search_trials':
            result = search_trials(
                lead_sponsor_name=param_dict.get('lead_sponsor_name'),
                disease_area=param_dict.get('disease_area'),
                overall_status=param_dict.get('overall_status'),
                location_country=param_dict.get('location_country')
            )
        elif api_path == '/trial_details':
            result = get_trial_details(nct_id=param_dict.get('nct_id'))
        elif api_path == '/inclusion_criteria':
            result = get_inclusion_criteria(nct_id=param_dict.get('nct_id'))
        elif api_path == '/exclusion_criteria':
            result = get_exclusion_criteria(nct_id=param_dict.get('nct_id'))
        else:
            result = {"error": f"Unsupported API path: {api_path}"}
        
        response_body = {
            'application/json': {
                'body': result
            }
        }
        
        action_response = {
            'actionGroup': action_group,
            'apiPath': api_path,
            'httpMethod': http_method,
            'httpStatusCode': 200,
            'responseBody': response_body
        }
        
        response = {
            'response': action_response,
            'messageVersion': message_version
        }
        
        logger.info(f"Response prepared")
        return response
        
    except KeyError as e:
        logger.error(f'Missing required field: {str(e)}')
        return {
            'statusCode': 400,
            'body': f'Error: Missing required field: {str(e)}'
        }
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return {
            'statusCode': 500,
            'body': f'Internal server error: {str(e)}'
        }

def search_trials(
    lead_sponsor_name: Optional[str] = None,
    disease_area: Optional[str] = None,
    overall_status: Optional[str] = None,
    location_country: Optional[str] = None
) -> List[Dict]:
    """Search for clinical trials based on criteria."""
    fields = [
        "protocolSection.identificationModule.nctId",
        "protocolSection.identificationModule.briefTitle",
    ]
    params = {"format": "json", "fields": ",".join(fields), "pageSize": 10}
    
    if disease_area:
        params["query.cond"] = disease_area.replace(" ", "+")
    if lead_sponsor_name:
        params["query.lead"] = lead_sponsor_name.replace(" ", "+")
    if location_country:
        params["query.locn"] = location_country.replace(" ", "+")
    if overall_status:
        params["filter.overallStatus"] = overall_status.upper()
    
    logger.info(f"Searching trials with params: {params}")
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    trials = []
    for study in data.get("studies", []):
        nct_id = get_nested_value(study, ["protocolSection", "identificationModule", "nctId"])
        trial = {
            "nct_id": nct_id,
            "brief_title": get_nested_value(study, ["protocolSection", "identificationModule", "briefTitle"]),
            "url": f"https://clinicaltrials.gov/study/{nct_id}"
        }
        trials.append(trial)
    
    logger.info(f"Found {len(trials)} trials")
    return trials

def get_trial_details(nct_id: str) -> Dict:
    """Get detailed information for a specific clinical trial."""
    fields = [
        "protocolSection.identificationModule.nctId",
        "protocolSection.identificationModule.briefTitle",
        "protocolSection.statusModule.overallStatus",
        "protocolSection.conditionsModule.conditions",
        "protocolSection.designModule.phases",
        "protocolSection.sponsorCollaboratorsModule.leadSponsor",
        "protocolSection.statusModule.startDateStruct",
        "protocolSection.statusModule.primaryCompletionDateStruct"
    ]
    
    params = {"format": "json", "fields": ",".join(fields), "query.id": nct_id}
    logger.info(f"Getting trial details for {nct_id}")
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if not data.get("studies"):
        logger.warning(f"Trial with NCT ID {nct_id} not found")
        return {"error": f"Trial with NCT ID {nct_id} not found"}
    
    study = data["studies"][0]
    return {
        "nct_id": get_nested_value(study, ["protocolSection", "identificationModule", "nctId"]),
        "brief_title": get_nested_value(study, ["protocolSection", "identificationModule", "briefTitle"]),
        "url": f"https://clinicaltrials.gov/study/{nct_id}",
        "status": get_nested_value(study, ["protocolSection", "statusModule", "overallStatus"]),
        "phase": get_first_item(study, ["protocolSection", "designModule", "phases"]),
        "conditions": get_nested_value(study, ["protocolSection", "conditionsModule", "conditions"], []),
        "sponsor": get_nested_value(study, ["protocolSection", "sponsorCollaboratorsModule", "leadSponsor", "name"]),
        "start_date": get_nested_value(study, ["protocolSection", "statusModule", "startDateStruct", "date"]),
        "completion_date": get_nested_value(study, ["protocolSection", "statusModule", "primaryCompletionDateStruct", "date"])
    }

def get_inclusion_criteria(nct_id: str) -> Dict:
    """Get inclusion criteria for a clinical trial."""
    params = {"format": "json", "fields": "protocolSection.eligibilityModule.eligibilityCriteria", "query.id": nct_id}
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if not data.get("studies"):
        return {"error": f"Trial with NCT ID {nct_id} not found"}
    
    try:
        eligibility_criteria = data["studies"][0]["protocolSection"]["eligibilityModule"]["eligibilityCriteria"]
        parts = eligibility_criteria.split("Exclusion Criteria:", 1)
        inclusion_text = parts[0].replace("Inclusion Criteria:", "").strip()
        
        # Format as numbered list
        inclusions = [item.strip() for item in inclusion_text.split('\n') if item.strip()]
        formatted = [f"{i+1}. {item}" for i, item in enumerate(inclusions)]
        
        return {"inclusion_criteria": formatted}
    except Exception as e:
        logger.error(f"Error processing inclusion criteria: {str(e)}")
        return {"error": "Could not extract inclusion criteria"}

def get_exclusion_criteria(nct_id: str) -> Dict:
    """Get exclusion criteria for a clinical trial."""
    params = {"format": "json", "fields": "protocolSection.eligibilityModule.eligibilityCriteria", "query.id": nct_id}
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if not data.get("studies"):
        return {"error": f"Trial with NCT ID {nct_id} not found"}
    
    try:
        eligibility_criteria = data["studies"][0]["protocolSection"]["eligibilityModule"]["eligibilityCriteria"]
        if "Exclusion Criteria:" in eligibility_criteria:
            exclusion_text = eligibility_criteria.split("Exclusion Criteria:", 1)[1].strip()
            
            # Format as numbered list
            exclusions = [item.strip() for item in exclusion_text.split('\n') if item.strip()]
            formatted = [f"{i+1}. {item}" for i, item in enumerate(exclusions)]
            
            return {"exclusion_criteria": formatted}
        else:
            return {"error": "No exclusion criteria found"}
    except Exception as e:
        logger.error(f"Error processing exclusion criteria: {str(e)}")
        return {"error": "Could not extract exclusion criteria"}

def get_nested_value(obj, path, default=None):
    """Get a value from a nested dictionary using a path of keys."""
    current = obj
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current

def get_first_item(obj, path, field=None):
    """Get the first item from a list in a nested structure."""
    value = get_nested_value(obj, path, [])
    if not value or not isinstance(value, list) or len(value) == 0:
        return None
    
    if field:
        return value[0].get(field)
    return value[0]