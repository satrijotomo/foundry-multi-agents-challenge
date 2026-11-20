from __future__ import annotations

import asyncio
import json
import re
import time
from typing import Any

from .models import AgentFinding, RouteDecision
from .tools import run_tool


class ConfiguredOrchestrator:
    def __init__(self, config: dict[str, Any], client: Any | None = None, mock: bool = False):
        self.config = config
        self.client = client
        self.mock = mock

    async def route(self, question: str, mode: str) -> RouteDecision:
        if self.mock or mode == "deterministic":
            return self._deterministic_route(question)

        catalog = {
            key: {"name": value["name"], "description": value["description"]}
            for key, value in self.config["agents"].items()
        }
        agent = self.client.create_agent(
            name=self.config["router"]["name"],
            instructions=self.config["router"]["instructions"],
        )
        prompt = f"Available specialists:\n{json.dumps(catalog, indent=2)}\n\nUser question:\n{question}"
        response = await agent.run(prompt)
        payload = self._extract_json(str(response))
        decision = RouteDecision.model_validate(payload)
        allowed = set(catalog)
        decision.selected_agents = [key for key in decision.selected_agents if key in allowed]
        if not decision.selected_agents:
            return self._deterministic_route(question)
        return decision

    async def run_specialists(self, question: str, selected: list[str]) -> list[AgentFinding]:
        return await asyncio.gather(*(self._run_specialist(key, question) for key in selected))

    async def synthesize(self, question: str, findings: list[AgentFinding]) -> str:
        if self.mock:
            headings = "\n\n".join(
                f"### {f.agent_name}\n{f.output}" for f in findings
            )
            return (
                "## Recommendation\n"
                "Prioritize the opportunities supported by the combined evidence, begin with a limited pilot, "
                "and validate eligibility and customer-level authorization before action.\n\n"
                f"{headings}\n\n"
                "## Limitations\nThe package is using synthetic hackathon evidence."
            )

        advisor = self.client.create_agent(
            name=self.config["strategy"]["name"],
            instructions=self.config["strategy"]["instructions"],
        )
        payload = [f.model_dump() for f in findings]
        prompt = f"User question:\n{question}\n\nSpecialist findings:\n{json.dumps(payload, indent=2)}"
        return str(await advisor.run(prompt))

    async def _run_specialist(self, key: str, question: str) -> AgentFinding:
        definition = self.config["agents"][key]
        started = time.perf_counter()
        evidence = await asyncio.to_thread(run_tool, definition["tool"], question)

        if self.mock:
            output = self._mock_analysis(key, evidence)
        else:
            agent = self.client.create_agent(
                name=definition["name"],
                instructions=definition["instructions"],
            )
            prompt = f"Question:\n{question}\n\nTool evidence:\n{json.dumps(evidence, indent=2)}"
            output = str(await agent.run(prompt))

        duration_ms = int((time.perf_counter() - started) * 1000)
        return AgentFinding(
            agent_key=key,
            agent_name=definition["name"],
            output=output,
            evidence=evidence,
            duration_ms=duration_ms,
        )

    def _deterministic_route(self, question: str) -> RouteDecision:
        text = question.lower()
        keyword_map = {
            "sales": ["sales", "revenue", "product", "category", "margin", "units", "selling", "performance"],
            "credit": ["credit", "risk", "score", "afford", "financing", "repayment", "delinquency", "low-risk"],
            "market": ["market", "trend", "competitor", "external", "benchmark", "demand", "outlook"],
        }
        selected = [key for key, words in keyword_map.items() if any(word in text for word in words)]
        if not selected:
            selected = ["sales"]
        return RouteDecision(
            selected_agents=selected,
            reason="Selected by transparent keyword rules for the hackathon deterministic mode.",
        )

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        candidate = fenced.group(1) if fenced else text[text.find("{"): text.rfind("}") + 1]
        return json.loads(candidate)

    @staticmethod
    def _mock_analysis(key: str, evidence: dict[str, Any]) -> str:
        records = evidence["records"]
        if key == "sales":
            best = max(records, key=lambda x: (x["growth_pct"], x["margin_pct"]))
            return f"{best['category']} has the strongest growth signal at {best['growth_pct']}% with {best['margin_pct']}% margin [{best['evidence']}]."
        if key == "credit":
            best = max(records, key=lambda x: x["avg_score"])
            return f"{best['segment']} has the strongest sample credit profile with average score {best['avg_score']} and {best['delinquency_pct']}% delinquency [{best['evidence']}]."
        return " ".join(f"{r['observation']} [{r['evidence']}]" for r in records[:2])
