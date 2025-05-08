# Agent Builder Prompts Documentation

## Supervisor Agent Prompts

### Router Supervisor
**File:** `build-prompt-supervisor-router.txt`
**Purpose:** Instructions for a routing-only supervisor agent
**Key Points:**
- Routes queries to appropriate agents
- Never modifies or summarizes responses
- Never combines information from multiple agents
- Routes to web-agent and clinical-agent

### General Supervisor
**File:** `build-prompt-supervisor.txt`
**Purpose:** Instructions for a general supervisor agent that can combine information
**Key Points:**
- Preserves and includes all reference information
- Maintains URLs, IDs, and other reference data
- Formats responses to show both content and sources

## Web Search Agent Prompts

### Web Search
**File:** `build-prompt-web-search.txt`
**Purpose:** Instructions for web search functionality
**Key Points:**
- Always preserves and includes ALL reference information
- Never removes or modifies reference information
- Always formats response to clearly show sources
- Checks for and includes:
  * URLs from brief_title fields
  * Source links
  * Any other reference information

## Multi-Agent Collaboration

### Current Multi-Agent Instructions
**File:** `current-multi-agent.txt`
**Purpose:** Current instructions for sub-agents in multi-agent collaboration
**Key Points:**
- Web Agent:
  * Executes web searches
  * Preserves all reference information
  * Shows sources clearly
  * Includes URLs and other reference data

- Clinical Agent:
  * Handles clinical trial queries
  * Uses closest_trials and search_trials tools appropriately
  * Always includes NCT IDs and clinicaltrials.gov links
  * Formats links as: https://clinicaltrials.gov/ct2/show/{nct_id}
  * Never modifies trial information

## Clinical Agent Prompts

### Clinical Trials
**File:** `build-prompt-clinical.txt`
**Purpose:** Instructions for clinical trial information handling
**Key Points:**
- Always includes NCT IDs and clinicaltrials.gov links
- Specific formatting for trial information
- Critical requirement to include reference URLs
- Proper handling of closest trials search

## Notes
- All prompts emphasize the importance of preserving reference information
- Each agent has specific formatting requirements
- Supervisor agents have different roles (routing vs. combining information)
- Multi-agent collaboration focuses on sub-agent behavior
- Current implementation uses specific formats for URLs and NCT IDs 