from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import streamlit as st
import yaml
from dotenv import load_dotenv

from src.models import RunResult
from src.orchestrator import ConfiguredOrchestrator
from src.trace import write_trace

load_dotenv()
st.set_page_config(page_title="Contoso Multi-Agent Lab", page_icon="🧭", layout="wide")

CONFIG_PATH = Path("config/agents.yaml")


def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def build_foundry_client():
    from agent_framework.foundry import FoundryChatClient
    from azure.identity.aio import AzureCliCredential

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_MODEL_DEPLOYMENT"]
    return FoundryChatClient(
        project_endpoint=endpoint,
        model=model,
        credential=AzureCliCredential(),
    )


async def execute(question: str, mock: bool, routing: str) -> RunResult:
    config = load_config()
    client = None if mock else build_foundry_client()
    orchestrator = ConfiguredOrchestrator(config=config, client=client, mock=mock)
    route = await orchestrator.route(question, routing)
    findings = await orchestrator.run_specialists(question, route.selected_agents)
    answer = await orchestrator.synthesize(question, findings)
    result = RunResult(
        question=question,
        routing_mode="mock/deterministic" if mock else routing,
        route=route,
        findings=findings,
        final_answer=answer,
    )
    result.trace_file = write_trace(result.model_dump())
    return result


if "result" not in st.session_state:
    st.session_state.result = None

st.title("Contoso Multi-Agent Strategy Lab")
st.caption("Configuration-led orchestration with specialist agents, evidence, and trace inspection")

with st.sidebar:
    st.header("Run settings")
    mock = st.toggle("Mock mode", value=True, help="Uses local synthetic data and does not require Azure.")
    routing = st.radio(
        "Routing mode",
        options=["generative", "deterministic"],
        index=0,
        disabled=mock,
        help="Mock mode always uses transparent deterministic routing.",
    )
    st.divider()
    st.subheader("Agent catalog")
    config = load_config()
    for key, agent in config["agents"].items():
        with st.expander(agent["name"]):
            st.write(agent["description"])
            st.caption(f"Tool: {agent['tool']}")

examples = {
    "Choose an example": "",
    "Sales": "What are our highest-revenue product categories?",
    "Credit": "Which customer segment has the strongest credit profile?",
    "Market": "What external trends are affecting premium electronics?",
    "Sales + Credit": "Which premium products should we promote to low-risk customers?",
    "Cross-domain": "What should Contoso prioritize based on sales, credit, and market evidence?",
}
selected_example = st.selectbox("Example question", list(examples))
default_question = examples[selected_example]
question = st.text_area(
    "Ask the strategy advisor",
    value=default_question,
    height=110,
    placeholder="Enter a sales, credit, market, or cross-domain question...",
)

run = st.button("Run multi-agent analysis", type="primary", use_container_width=True)
if run:
    if not question.strip():
        st.warning("Enter a question before running the analysis.")
    else:
        try:
            with st.status("Running orchestration...", expanded=True) as status:
                st.write("Selecting specialist agents")
                result = asyncio.run(execute(question.strip(), mock, routing))
                st.write("Collecting specialist findings")
                st.write("Synthesizing the recommendation")
                status.update(label="Analysis complete", state="complete")
            st.session_state.result = result
        except KeyError as exc:
            st.error(f"Missing environment setting: {exc.args[0]}")
        except Exception as exc:
            st.exception(exc)

result = st.session_state.result
if result:
    st.divider()
    st.subheader("Routing decision")
    cols = st.columns(max(1, len(result.route.selected_agents)))
    config = load_config()
    for col, key in zip(cols, result.route.selected_agents):
        with col:
            st.info(config["agents"][key]["name"])
    st.caption(result.route.reason)

    st.subheader("Final recommendation")
    st.markdown(result.final_answer)

    st.subheader("Specialist findings")
    for finding in result.findings:
        with st.expander(f"{finding.agent_name} · {finding.duration_ms} ms", expanded=True):
            st.markdown(finding.output)
            st.markdown("**Evidence returned by tool**")
            st.json(finding.evidence)

    trace_payload = result.model_dump()
    trace_json = json.dumps(trace_payload, indent=2, default=str)
    left, right = st.columns([2, 1])
    with left:
        with st.expander("Execution trace"):
            st.json(trace_payload)
    with right:
        st.download_button(
            "Download trace JSON",
            data=trace_json,
            file_name="multi-agent-trace.json",
            mime="application/json",
            use_container_width=True,
        )
        st.caption(f"Server trace: {result.trace_file}")
