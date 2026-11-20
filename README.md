# Challenge 5: Configuration-Led Multi-Agent Orchestration

Build a multi-agent solution using Microsoft Foundry models and Microsoft Agent Framework without Copilot Studio, Logic Apps, or a visual workflow designer.

Participants configure specialist agents in YAML. A supplied Python runtime selects the appropriate agents, runs them in parallel, and synthesizes one evidence-grounded response.

## Learning objectives

By the end of this challenge, you will be able to:

1. Define clear responsibilities for specialist agents.
2. Influence routing through agent names, descriptions, and instructions.
3. Connect agents to internal-data and external-research tools.
4. Compare deterministic and generative routing.
5. Run multiple specialists concurrently for cross-domain questions.
6. Inspect routing decisions, agent outputs, timing, assumptions, and limitations.
7. Recognize when a configuration-led prototype should become a production workflow.

## Scenario

Contoso wants one strategy assistant that can answer questions spanning:

- Sales performance
- Customer credit risk
- External market conditions

The solution uses four roles:

- **Router**: Selects the minimum set of relevant specialists.
- **Sales Operations Agent**: Analyzes internal sales data.
- **Credit Risk Agent**: Analyzes customer credit and financing suitability.
- **Market Research Agent**: Analyzes external market evidence supplied through an approved tool.
- **Strategy Advisor**: Synthesizes the specialist findings into one response.

The router and strategy advisor are runtime roles. Participants primarily configure the three specialists in `config/agents.yaml`.

## Architecture

```text
User question
    |
    v
Router agent or deterministic route configuration
    |
    +-------------------+-------------------+
    |                   |                   |
    v                   v                   v
Sales agent        Credit agent        Market agent
    |                   |                   |
Sales tool          Credit tool         Market tool
    +-------------------+-------------------+
                        |
                        v
                 Strategy advisor
                        |
                        v
              Consolidated response + trace
```

## Prerequisites

- Python 3.11 or later
- Azure subscription and Microsoft Foundry project
- A deployed chat model in the Foundry project
- Azure CLI authenticated with `az login`
- Permission to invoke the model deployment

For a no-subscription dry run, use `--mock`. This validates the learning flow with local sample data and deterministic routing.

## Setup

### 1. Create the environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure Foundry

Edit `.env`:

```dotenv
FOUNDRY_PROJECT_ENDPOINT=https://YOUR-FOUNDRY-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
FOUNDRY_MODEL_DEPLOYMENT=YOUR-MODEL-DEPLOYMENT
```

The sample uses `AzureCliCredential`. Run:

```bash
az login
```

### 3. Test locally

```bash
python app.py --mock --question "Which premium products should we target to customers with strong credit profiles?"
```

### 4. Run with Foundry

```bash
python app.py --question "Which premium products should we target to customers with strong credit profiles?"
```

## Participant tasks

### Task 1: Inspect the agent contracts

Open `config/agents.yaml`. For each specialist, identify:

- Its domain
- When it should and should not be selected
- Its tool
- Its expected output structure

### Task 2: Improve an ambiguous description

Temporarily replace the Credit Risk Agent description with:

> Helps with customer information.

Run these questions and observe the route:

```bash
python app.py --mock --question "Which customer segment has the highest average credit score?"
python app.py --mock --question "What are our best-selling premium products?"
```

Restore and improve the description so that the router can distinguish credit questions from sales questions.

### Task 3: Test single-domain routing

Run:

```bash
python app.py --mock --question "What are our highest-revenue product categories?"
python app.py --mock --question "Which customer segment has the strongest credit profile?"
python app.py --mock --question "What external trends are affecting premium electronics?"
```

Expected result: only the relevant specialist is selected for each question.

### Task 4: Test cross-domain orchestration

Run:

```bash
python app.py --mock --question "Based on sales performance and credit profiles, which premium products should we promote to low-risk customers?"
```

Expected result:

1. Sales and Credit agents are selected.
2. They execute concurrently.
3. The Strategy Advisor correlates their findings.
4. The trace records selection, timing, findings, assumptions, and limitations.

### Task 5: Compare routing modes

Generative routing:

```bash
python app.py --question "Which products should we prioritize considering internal performance and market trends?"
```

Deterministic routing:

```bash
python app.py --mock --routing deterministic --question "Which products should we prioritize considering internal performance and market trends?"
```

Discuss:

- Which mode is more adaptable?
- Which is easier to predict and govern?
- Which would you use for a regulated process?

### Task 6: Inspect the trace

Open the JSON file created in `traces/`. Identify:

- Selected agents
- Routing reason
- Tool evidence
- Specialist findings
- Execution duration
- Final synthesis
- Limitations

## Suggested test questions

| Type | Question |
|---|---|
| Sales | What categories produce the most revenue? |
| Credit | Which segment has the lowest credit risk? |
| Market | What trends are shaping premium electronics demand? |
| Sales + Credit | Which high-performing products fit low-risk customer segments? |
| Sales + Market | Which strong internal products align with external growth trends? |
| Cross-domain | What should Contoso prioritize based on sales, credit, and market evidence? |

## Success criteria

Your solution is successful when:

- Single-domain questions invoke one relevant specialist.
- Cross-domain questions invoke the needed specialists without invoking every agent by default.
- Specialist outputs cite tool evidence and state limitations.
- The final response distinguishes internal evidence from external evidence.
- A trace is generated for each execution.
- Changing agent descriptions changes routing behavior without changing Python.

## Production discussion

This package is intentionally optimized for a hackathon. Before production, consider:

- Replace sample tools with governed APIs, Fabric Data Agent endpoints, MCP servers, or approved search services.
- Use managed identity when hosted.
- Apply user-level authorization before retrieving data.
- Add prompt-injection defenses for untrusted content.
- Add structured output validation and retries.
- Add OpenTelemetry and Foundry tracing.
- Add human approval before consequential actions.
- Add evaluation datasets for routing accuracy and answer groundedness.
- Use an explicit Agent Framework workflow when sequence, checkpoints, approvals, or recovery must be guaranteed.

## Optional extensions

1. Replace one sample tool with a real Fabric-backed API.
2. Add a fourth specialist without changing `src/orchestrator.py`.
3. Add an approval step for recommendations above a risk threshold.
4. Add a routing evaluation dataset.
5. Host the app behind an API or lightweight web interface.

## Optional interactive UI

The package includes a simple Streamlit interface for customer workshops. It provides:

- Mock or Foundry-backed execution
- Example questions
- Routing-mode selection
- Visible selected-agent cards
- Expandable specialist findings and tool evidence
- Final synthesized recommendation
- Execution-trace viewer and JSON download

Start it with:

```bash
streamlit run ui.py
```

The browser opens at the local Streamlit address. Begin in **Mock mode** so participants can explore the complete flow without Azure configuration. Turn off Mock mode to use the Foundry project settings from `.env`.
