import asyncio
from pathlib import Path

import yaml

from src.orchestrator import ConfiguredOrchestrator


def load_config():
    return yaml.safe_load(Path("config/agents.yaml").read_text(encoding="utf-8"))


def test_cross_domain_route():
    orchestrator = ConfiguredOrchestrator(load_config(), mock=True)
    result = asyncio.run(orchestrator.route(
        "Which products should we promote to low-risk customers?", "deterministic"
    ))
    assert "sales" in result.selected_agents
    assert "credit" in result.selected_agents
