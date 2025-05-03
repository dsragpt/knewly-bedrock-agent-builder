import json
import os
import urllib.parse
import urllib.request
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# OpenFDA API Base URL
OPENFDA_BASE_URL = "https://api.fda.gov"

# Optional: If you have an API key, you can set it as an environment variable
API_KEY = os.environ.get("OPENFDA_API_KEY", "")

# Maximum response size in bytes (set to 20KB to provide some buffer)
MAX_RESPONSE_SIZE = 20 * 1024

def build_url(path, params=None):
    """Build the OpenFDA API URL"""
    url = f"{OPENFDA_BASE_URL}{path}"
    
    if params:
        # Add API key if available
        if API_KEY:
            params["api_key"] = API_KEY
            
        # Convert params to URL query string
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"
    elif API_KEY:
        # If no params but we have an API key
        url = f"{url}?api_key={API_KEY}"
        
    return url

def make_request(url):
    """Make a request to the OpenFDA API"""
    try:
        logger.info(f"Making request to: {url}")
        with urllib.request.urlopen(url) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)
    except Exception as e:
        logger.error(f"Error making request: {str(e)}")
        return {
            "meta": {
                "status": 500,
                "error": {"message": f"Error: {str(e)}"}
            },
            "results": []
        }

def limit_response_size(response_data, max_results=3, endpoint_type=None):
    """
    Limit the size of the response by trimming results
    
    Args:
        response_data: The original response data
        max_results: Maximum number of results to include
        endpoint_type: Type of endpoint for specialized handling
        
    Returns:
        Limited response data
    """
    # Get a copy of the original data
    limited_data = {
        "meta": response_data.get("meta", {}),
        "results": []
    }
    
    # Add summary of total results
    if "results" in response_data:
        total_results = len(response_data["results"])
        limited_data["meta"]["total_results"] = total_results
        limited_data["meta"]["results_shown"] = min(max_results, total_results)
        
        # Only include the specified number of results
        limited_data["results"] = response_data["results"][:max_results]
        
        # Apply endpoint-specific limiting
        if endpoint_type == "drug_event":
            limit_drug_event_results(limited_data, response_data)
        elif endpoint_type == "device_event":
            limit_device_event_results(limited_data, response_data)
        elif endpoint_type == "classification":
            limit_classification_results(limited_data)
        else:
            # Generic field limiting - keep only top-level fields and first-level child objects
            limit_generic_results(limited_data)
    
    return limited_data

def limit_drug_event_results(limited_data, original_data):
    """Limit fields for drug event results"""
    for i, result in enumerate(limited_data["results"]):
        # Keep only essential fields
        keys_to_keep = ["receivedate", "safetyreportid", "serious", "seriousnessdeath", "patient"]
        for key in list(result.keys()):
            if key not in keys_to_keep:
                result.pop(key, None)
        
        # Limit patient data
        if "patient" in result:
            patient = result["patient"]
            
            # Limit drug information
            if "drug" in patient:
                # Keep only first 2 drugs
                if isinstance(patient["drug"], list) and len(patient["drug"]) > 2:
                    patient["drug"] = patient["drug"][:2]
                    if i < len(original_data["results"]) and "patient" in original_data["results"][i]:
                        patient["drug_count_original"] = len(original_data["results"][i]["patient"]["drug"])
                
                # For each drug, keep only essential fields
                for drug in patient["drug"] if isinstance(patient["drug"], list) else [patient["drug"]]:
                    keys_to_keep = ["medicinalproduct", "drugindication", "drugcharacterization"]
                    for key in list(drug.keys()):
                        if key not in keys_to_keep:
                            drug.pop(key, None)
            
            # Limit reaction information
            if "reaction" in patient:
                # Keep only first 3 reactions
                if isinstance(patient["reaction"], list) and len(patient["reaction"]) > 3:
                    patient["reaction"] = patient["reaction"][:3]
                    if i < len(original_data["results"]) and "patient" in original_data["results"][i]:
                        patient["reaction_count_original"] = len(original_data["results"][i]["patient"]["reaction"])

def limit_device_event_results(limited_data, original_data):
    """Limit fields for device event results"""
    for i, result in enumerate(limited_data["results"]):
        # Keep only essential fields
        keys_to_keep = ["report_number", "date_received", "event_type", "device"]
        for key in list(result.keys()):
            if key not in keys_to_keep:
                result.pop(key, None)
        
        # Limit device information
        if "device" in result:
            # Keep only first 2 devices
            if isinstance(result["device"], list) and len(result["device"]) > 2:
                result["device"] = result["device"][:2]
                if i < len(original_data["results"]):
                    result["device_count_original"] = len(original_data["results"][i]["device"])
            
            # For each device, keep only essential fields
            for device in result["device"] if isinstance(result["device"], list) else [result["device"]]:
                keys_to_keep = ["brand_name", "generic_name", "device_event_type", "device_report_product_code"]
                for key in list(device.keys()):
                    if key not in keys_to_keep:
                        device.pop(key, None)

def limit_classification_results(limited_data):
    """Limit fields for device classification results"""
    for result in limited_data["results"]:
        # Keep only essential fields
        keys_to_keep = ["device_name", "device_class", "medical_specialty_description", "regulation_number", "product_code"]
        for key in list(result.keys()):
            if key not in keys_to_keep:
                result.pop(key, None)

def limit_generic_results(limited_data):
    """Generic field limiting for all other endpoints"""
    for result in limited_data["results"]:
        # Keep a maximum of 8 top-level keys per result
        if len(result) > 8:
            # Sort keys by length (shorter keys are likely more important metadata)
            sorted_keys = sorted(result.keys(), key=lambda k: len(str(result[k])))
            # Keep only first 8 keys
            keys_to_remove = sorted_keys[8:]
            for key in keys_to_remove:
                result.pop(key, None)
        
        # Limit nested objects
        for key, value in result.items():
            if isinstance(value, dict) and len(value) > 5:
                # Keep only first 5 keys in nested dictionaries
                nested_keys = list(value.keys())[:5]
                result[key] = {k: value[k] for k in nested_keys}
            elif isinstance(value, list) and len(value) > 3:
                # Keep only first 3 items in nested lists
                result[key] = value[:3]

def extract_parameters(parameters):
    """Extract search, limit, and skip parameters from the parameters list"""
    search = None
    limit = 10
    skip = 0
    
    for param in parameters:
        if param["name"] == "search":
            search = param["value"]
        elif param["name"] == "limit":
            try:
                limit = int(param["value"])
            except (ValueError, TypeError):
                limit = 10
        elif param["name"] == "skip":
            try:
                skip = int(param["value"])
            except (ValueError, TypeError):
                skip = 0
    
    return search, limit, skip

def handle_endpoint(endpoint_path, parameters, endpoint_type=None):
    """
    Handle requests for any OpenFDA endpoint
    
    Args:
        endpoint_path: The path to the endpoint (e.g., /drug/event.json)
        parameters: List of parameters from the Bedrock agent
        endpoint_type: Type of endpoint for specialized handling
        
    Returns:
        Formatted response
    """
    try:
        # Extract parameters
        search, limit, skip = extract_parameters(parameters)
        
        # Build request params
        params = {}
        if search:
            params["search"] = search
        params["limit"] = limit
        if skip > 0:
            params["skip"] = skip
        
        # Make request to OpenFDA API
        url = build_url(endpoint_path, params)
        response = make_request(url)
        
        # Limit response size
        limited_response = limit_response_size(response, max_results=3, endpoint_type=endpoint_type)
        
        # Convert to JSON string
        response_json = json.dumps(limited_response)
        
        # Check if still too large and further limit if needed
        if len(response_json) > MAX_RESPONSE_SIZE:
            # Try more aggressive limiting
            limited_response = limit_response_size(response, max_results=1, endpoint_type=endpoint_type)
            response_json = json.dumps(limited_response)
            
            # If still too large, return a summary instead
            if len(response_json) > MAX_RESPONSE_SIZE:
                summary = {
                    "meta": response.get("meta", {}),
                    "summary": f"Found {len(response.get('results', []))} results for the query. Response was too large to return in full."
                }
                response_json = json.dumps(summary)
        
        return {
            "statusCode": 200,
            "body": response_json
        }
    except Exception as e:
        logger.error(f"Error in handle_endpoint: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": f"Error processing request: {str(e)}"
            })
        }

def lambda_handler(event, context):
    """Main Lambda handler function"""
    try:
        # Log the entire event for debugging
        logger.info(f"Event: {json.dumps(event)}")
        
        # Extract relevant information from event
        action_group = event.get('actionGroup', '')
        api_path = event.get('apiPath', '')
        http_method = event.get('httpMethod', '')
        parameters = event.get('parameters', [])
        
        # Log extracted information
        logger.info(f"Action Group: {action_group}")
        logger.info(f"API Path: {api_path}")
        logger.info(f"HTTP Method: {http_method}")
        logger.info(f"Parameters: {parameters}")
        
        # Map API paths to endpoint paths and types
        endpoint_mapping = {
            # Drug endpoints
            "/drug/event": ("/drug/event.json", "drug_event"),
            "/drug/label": ("/drug/label.json", None),
            "/drug/ndc": ("/drug/ndc.json", None),
            "/drug/enforcement": ("/drug/enforcement.json", None),
            "/drug/drugsfda": ("/drug/drugsfda.json", None),
            "/drug/shortages": ("/drug/shortages.json", None),
            
            # Device endpoints
            "/device/event": ("/device/event.json", "device_event"),
            "/device/classification": ("/device/classification.json", "classification"),
            "/device/510k": ("/device/510k.json", None),
            "/device/enforcement": ("/device/enforcement.json", None),
            "/device/pma": ("/device/pma.json", None),
            "/device/registrationlisting": ("/device/registrationlisting.json", None),
            "/device/recall": ("/device/recall.json", None)
        }
        
        # Handle .json suffix in API path
        clean_api_path = api_path.replace(".json", "")
        
        # Process based on API path
        if clean_api_path in endpoint_mapping:
            endpoint_path, endpoint_type = endpoint_mapping[clean_api_path]
            result = handle_endpoint(endpoint_path, parameters, endpoint_type)
        else:
            # List all supported endpoints
            supported_endpoints = list(endpoint_mapping.keys())
            result = {
                "statusCode": 400,
                "body": json.dumps({
                    "error": f"Unsupported API path: {api_path}",
                    "supported_paths": supported_endpoints
                })
            }
        
        # Extract response information
        status_code = result.get("statusCode", 200)
        body = result.get("body", "{}")
        
        # Format response for Bedrock agent
        response = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "apiPath": api_path,
                "httpMethod": http_method,
                "httpStatusCode": status_code,
                "responseBody": {
                    "application/json": {
                        "body": body
                    }
                }
            }
        }
        
        # Ensure final response is within size limits
        response_json = json.dumps(response)
        response_size = len(response_json.encode('utf-8'))
        logger.info(f"Response size: {response_size} bytes")
        
        if response_size > 25 * 1024:  # 25KB limit
            logger.warning(f"Response size exceeds 25KB: {response_size} bytes")
            # Create a minimal response with error message
            minimal_response = {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "apiPath": api_path,
                    "httpMethod": http_method,
                    "httpStatusCode": 413,  # Request Entity Too Large
                    "responseBody": {
                        "application/json": {
                            "body": json.dumps({
                                "error": "Response exceeded maximum size limit",
                                "message": "Try a more specific query to reduce response size"
                            })
                        }
                    }
                }
            }
            return minimal_response
        
        logger.info(f"Response: {json.dumps(response)}")
        return response
    except Exception as e:
        logger.error(f"Unhandled error in lambda_handler: {str(e)}")
        # Return a formatted error response that Bedrock can handle
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get('actionGroup', ''),
                "apiPath": event.get('apiPath', ''),
                "httpMethod": event.get('httpMethod', ''),
                "httpStatusCode": 500,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps({
                            "error": f"Internal error: {str(e)}"
                        })
                    }
                }
            }
        }