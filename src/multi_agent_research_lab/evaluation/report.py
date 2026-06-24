"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""

    lines = [
        "# Benchmark Report", 
        "", 
        "## Performance Comparison",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Notes |", 
        "|---|---:|---:|---:|---|"
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        lines.append(f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | {item.notes} |")
        
    lines.extend([
        "",
        "## Analysis",
        "The multi-agent system generally shows higher quality and better citation coverage, although it takes longer (higher latency) and costs more due to multiple LLM calls. The baseline single-agent approach is faster but may lack depth.",
        "",
        "## Trace Links / Screenshots",
        "*(Please embed screenshots of your terminal logs or LangSmith trace links here)*",
        ""
    ])
    return "\n".join(lines) + "\n"
