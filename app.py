from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.models import RunResult
from src.orchestrator import ConfiguredOrchestrator
from src.trace import write_trace


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


async def main() -> None:
    parser = argparse.ArgumentParser(description="Configuration-led multi-agent hackathon runtime")
    parser.add_argument("--question", required=True)
    parser.add_argument("--routing", choices=["generative", "deterministic"], default="generative")
    parser.add_argument("--mock", action="store_true", help="Use synthetic data and no Foundry connection")
    args = parser.parse_args()

    load_dotenv()
    config = yaml.safe_load(Path("config/agents.yaml").read_text(encoding="utf-8"))
    client = None if args.mock else build_foundry_client()
    orchestrator = ConfiguredOrchestrator(config=config, client=client, mock=args.mock)

    route = await orchestrator.route(args.question, args.routing)
    findings = await orchestrator.run_specialists(args.question, route.selected_agents)
    answer = await orchestrator.synthesize(args.question, findings)

    result = RunResult(
        question=args.question,
        routing_mode="mock/deterministic" if args.mock else args.routing,
        route=route,
        findings=findings,
        final_answer=answer,
    )
    trace_path = write_trace(result.model_dump())
    result.trace_file = trace_path

    print(f"\nSelected agents: {', '.join(route.selected_agents)}")
    print(f"Routing reason: {route.reason}\n")
    print(answer)
    print(f"\nTrace: {trace_path}")


if __name__ == "__main__":
    asyncio.run(main())
