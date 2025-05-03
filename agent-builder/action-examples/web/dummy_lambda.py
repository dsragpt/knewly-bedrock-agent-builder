# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import http.client
import json
import logging
import os
import urllib.parse
import urllib.request

import boto3

log_level = os.environ.get("LOG_LEVEL", "INFO").strip().upper()
logging.basicConfig(format="[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
ACTION_GROUP_NAME = os.environ.get("ACTION_GROUP", "action_group_quick_start_laegh")
FUNCTION_NAMES = ["tavily-ai-search", "google-search"]


def is_env_var_set(env_var: str) -> bool:
    return env_var in os.environ and os.environ[env_var] not in ("", "0", "false", "False")


def get_from_secretstore_or_env(key: str) -> str:
    if is_env_var_set(key):
        logger.warning(f"getting value for {key} from environment var; recommended to use AWS Secrets Manager instead")
        return os.environ[key]

    session = boto3.session.Session()
    secrets_manager = session.client(service_name="secretsmanager", region_name=AWS_REGION)
    try:
        secret_value = secrets_manager.get_secret_value(SecretId=key)
    except Exception as e:
        logger.error(f"could not get secret {key} from secrets manager: {e}")
        raise e

    secret: str = secret_value["SecretString"]

    return secret


SERPER_API_KEY = get_from_secretstore_or_env("SERPER_API_KEY")
TAVILY_API_KEY = get_from_secretstore_or_env("TAVILY_API_KEY")


def extract_search_params(action_group, function, parameters):
    if action_group != ACTION_GROUP_NAME:
        logger.error(f"unexpected name '{action_group}'; expected valid action group name '{ACTION_GROUP_NAME}'")
        return None, None, None, None

    if function not in FUNCTION_NAMES:
        logger.error(f"unexpected function name '{function}'; valid function names are'{FUNCTION_NAMES}'")
        return None, None, None, None

    search_query = next(
        (param["value"] for param in parameters if param["name"] == "search_query"),
        None,
    )

    target_website = next(
        (param["value"] for param in parameters if param["name"] == "target_website"),
        None,
    )

    include_metadata = next(
        (param["value"] for param in parameters if param["name"] == "include_metadata"),
        True,
    )

    consolidate_results = next(
        (param["value"] for param in parameters if param["name"] == "consolidate_results"),
        False,
    )

    logger.debug(f"extract_search_params: {search_query=} {target_website=} {include_metadata=} {consolidate_results=}")

    return search_query, target_website, include_metadata, consolidate_results


def google_search(search_query: str, target_website: str = "") -> str:
    query = search_query
    if target_website:
        query += f" site:{target_website}"

    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({"q": query})
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

    search_type = "news"  # "news", "search",
    conn.request("POST", f"/{search_type}", payload, headers)
    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")


def create_consolidated_summary(results):
    """Create a consolidated summary from multiple search results"""
    if not results:
        return "No results found."
    
    # Sort results by score in descending order
    sorted_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
    
    # Create a summary that includes key points from each result
    summary_parts = []
    for i, result in enumerate(sorted_results, 1):
        title = result.get("title", "Untitled")
        content = result.get("content", "")
        url = result.get("url", "")
        
        # Take the first few sentences of content
        content_summary = ". ".join(content.split(". ")[:2]) + "."
        
        summary_parts.append(
            f"Source {i} ({url}): {title}\n"
            f"Summary: {content_summary}\n"
        )
    
    # Add a final note about sources
    summary_parts.append(
        f"\nThis information is compiled from {len(results)} sources. "
        "Please refer to the individual sources for complete information."
    )
    
    return "\n".join(summary_parts)


def tavily_ai_search(search_query: str, target_website: str = "", include_metadata: bool = True, consolidate_results: bool = False) -> str:
    logger.info(f"executing Tavily AI search with {search_query=}")

    base_url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": search_query,
        "search_depth": "advanced",
        "include_images": False,
        "include_answer": False,
        "include_raw_content": False,
        "max_results": 3,
        "include_domains": [target_website] if target_website else [],
        "exclude_domains": [],
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(base_url, data=data, headers=headers)

    try:
        response = urllib.request.urlopen(request)
        response_data = json.loads(response.read().decode("utf-8"))
        logger.debug(f"response from Tavily AI search {response_data=}")
        
        results = [
            {
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "url": result.get("url", ""),
                "score": result.get("score", 0.0)
            }
            for result in response_data.get("results", [])
        ]
        
        if consolidate_results:
            summary = create_consolidated_summary(results)
            if include_metadata:
                return json.dumps({
                    "summary": summary,
                    "results": results
                })
            else:
                return json.dumps({"TEXT": {"body": summary}})
        else:
            if include_metadata:
                return json.dumps({"results": results})
            else:
                return json.dumps({"TEXT": {"body": " ".join(result.get("content", "") for result in results)}})
    except urllib.error.HTTPError as e:
        logger.error(f"failed to retrieve search results from Tavily AI Search, error: {e.code}")
        return json.dumps({"error": f"Search failed with error code: {e.code}"})


def lambda_handler(event, _):  # type: ignore
    logging.debug(f"lambda_handler {event=}")

    action_group = event["actionGroup"]
    function = event["function"]
    parameters = event.get("parameters", [])

    logger.info(f"lambda_handler: {action_group=} {function=}")

    search_query, target_website, include_metadata, consolidate_results = extract_search_params(action_group, function, parameters)

    search_results: str = ""
    if function == "tavily-ai-search":
        search_results = tavily_ai_search(search_query, target_website, include_metadata, consolidate_results)
    elif function == "google-search":
        search_results = google_search(search_query, target_website)

    logger.debug(f"query results {search_results=}")

    # Parse the response to ensure it's in the correct format
    try:
        response_data = json.loads(search_results)
        if "results" in response_data or "summary" in response_data:
            # Structured response with metadata
            function_response_body = response_data
        else:
            # Simple text response
            function_response_body = {"TEXT": {"body": response_data.get("TEXT", {}).get("body", search_results)}}
    except json.JSONDecodeError:
        function_response_body = {"TEXT": {"body": search_results}}

    action_response = {
        "actionGroup": action_group,
        "function": function,
        "functionResponse": {"responseBody": function_response_body},
    }

    response = {"response": action_response, "messageVersion": event["messageVersion"]}

    logger.debug(f"lambda_handler: {response=}")

    return response
