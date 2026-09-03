# CO_ORDINATOR_AGENT

The central orchestrator of the DevOps Agents platform. It is the **sole external entry point** — all user requests go through this agent. It uses an LLM to reason over the request and delegates work to specialist sub-agents via HTTP tool calls.

---

## Responsibilities

- Accepts user prompts via REST API
- Propagates GitHub PAT tokens securely to sub-agents using Python `contextvars`
- Maintains conversation history and a separate audit trail across turns
- Uses LLM reasoning to decide which sub-agent(s) to invoke and in what order
- Normalizes and returns structured responses

---

## Architecture

```
POST /co_ordinator_agent
        │
        ▼
  CoOrdinatorAgent (LLM)
        │
        ├── yaml_agent_tool_call(prompt)       → HTTP → YAML_AGENT
        ├── github_agent_tool_call(prompt)     → HTTP → GITHUB_AGENT
        ├── terraform_agent_tool_call(prompt)  → HTTP → TERRAFORM_AGENT
        └── failure_agent_tool_call(prompt)    → HTTP → FAILURE_AGENT
```

The LLM reads each tool's description (`AgentDescriptionPrompt`) to decide routing — no hardcoded if/else logic.

---

## File Structure

```
CO_ORDINATOR_AGENT/
├── main.py                     # FastAPI app entry point
├── api.py                      # Route: POST /co_ordinator_agent
├── co_ordinator_agent.py       # CoOrdinatorAgent class definition
├── co_ord_config.py            # Loads sub-agent URLs from .env
├── co_ordinator_tools/
│   ├── agent_tools.py          # @tool wrappers for each sub-agent HTTP call
│   └── __init__.py
├── .env                        # Environment variables (not committed)
├── requirements.txt
└── .gitignore
```

---

## Environment Variables

Create a `.env` file in this directory:

```env
# Sub-agent service URLs
Github_agent_URL=http://localhost:8001/github_agent
YAML_agent_URL=http://localhost:8002/yaml_agent
Terraform_agent_URL=http://localhost:8003/terraform_agent
Failure_agent_URL=http://localhost:8004/failure_agent

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=<your_azure_openai_endpoint>
AZURE_OPENAI_API_KEY=<your_azure_openai_api_key>
AZURE_OPENAI_DEPLOYMENT=<your_deployment_name>
```

---

## API

### `POST /co_ordinator_agent`

**Request Body:**
```json
{
  "prompt": "Generate a CI/CD pipeline for my Python app in repo my-app",
  "pat_token": "<github_personal_access_token>"
}
```

**Response:**
```json
{
  "response": "Co-ordinator agent executed successfully",
  "raw": { ... },
  "is_json": true,
  "output": "..."
}
```

**Error (missing token):**
```json
{ "message": "No git token provided" }
```

---

## Tools (Sub-Agent Delegates)

| Tool Name | Delegates To | Passes PAT Token |
|---|---|---|
| `Github_Agent` | GITHUB_AGENT | Yes |
| `Yaml_Agent` | YAML_AGENT | No |
| `Terraform_Agent` | TERRAFORM_AGENT | No |
| `Failure_Agent` | FAILURE_AGENT | Yes |

---

## Memory & Context

| Provider | Purpose |
|---|---|
| `InMemoryHistoryProvider(load_messages=True)` | Maintains full conversation history across turns |
| `InMemoryHistoryProvider("audit", store_context_messages=True)` | Separate audit log of all context messages |

---

## Setup & Run

```bash
cd agents/CO_ORDINATOR_AGENT

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env   # then fill in values

# Start the service (ensure sub-agents are running first)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Example Usage

```bash
# Generate a CI pipeline
curl -X POST http://localhost:8000/co_ordinator_agent \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a GitHub Actions CI pipeline for a Python Flask app in repo my-flask-app on branch main",
    "pat_token": "<your_github_pat>"
  }'

# Provision Terraform infrastructure
curl -X POST http://localhost:8000/co_ordinator_agent \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Provision an Azure Web App in East US with resource group my-rg for repo my-app",
    "pat_token": "<your_github_pat>"
  }'
```

---

## Dependencies

See [requirements.txt](requirements.txt). Key packages:
- `fastapi`, `uvicorn` — API server
- `agent_framework` — agent runtime
- `vida` — internal SDK (prompts, config, adapters)
- `python-dotenv` — environment config
- `requests` — HTTP calls to sub-agents
