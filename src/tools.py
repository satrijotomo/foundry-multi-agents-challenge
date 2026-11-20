from __future__ import annotations

from typing import Any

SAMPLE_DATA: dict[str, list[dict[str, Any]]] = {
    "sales_data": [
        {"evidence": "SALES-01", "category": "Premium laptops", "revenue_m": 8.4, "growth_pct": 18, "margin_pct": 24},
        {"evidence": "SALES-02", "category": "Gaming monitors", "revenue_m": 5.7, "growth_pct": 26, "margin_pct": 21},
        {"evidence": "SALES-03", "category": "Entry tablets", "revenue_m": 6.1, "growth_pct": -4, "margin_pct": 9},
    ],
    "credit_data": [
        {"evidence": "CREDIT-01", "segment": "Established professionals", "avg_score": 752, "delinquency_pct": 1.4, "capacity": "high"},
        {"evidence": "CREDIT-02", "segment": "Small business owners", "avg_score": 704, "delinquency_pct": 3.8, "capacity": "medium-high"},
        {"evidence": "CREDIT-03", "segment": "New-to-credit", "avg_score": 641, "delinquency_pct": 7.9, "capacity": "low"},
    ],
    "market_data": [
        {"evidence": "MARKET-01", "observation": "Premium mobile-computing demand is growing among hybrid professionals.", "freshness": "sample"},
        {"evidence": "MARKET-02", "observation": "Gaming and creator displays show continued interest in high-refresh and color-accurate models.", "freshness": "sample"},
        {"evidence": "MARKET-03", "observation": "Entry tablets face pricing pressure and product substitution.", "freshness": "sample"},
    ],
}


def run_tool(tool_name: str, question: str) -> dict[str, Any]:
    """Return sample evidence. Replace this adapter with governed APIs or MCP tools."""
    if tool_name not in SAMPLE_DATA:
        raise ValueError(f"Unknown tool: {tool_name}")
    return {
        "tool": tool_name,
        "question": question,
        "notice": "Synthetic hackathon data; do not use for real decisions.",
        "records": SAMPLE_DATA[tool_name],
    }
