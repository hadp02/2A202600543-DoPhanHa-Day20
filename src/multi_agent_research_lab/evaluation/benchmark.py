"""Benchmark skeleton for single-agent vs multi-agent."""

from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a metric object."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    
    total_cost = 0.0
    for res in state.agent_results:
        cost = res.metadata.get("cost_usd", 0.0)
        total_cost += cost if cost is not None else 0.0
        
    error_count = len(state.errors)
    
    quality_score = 5.0
    if state.final_answer:
        if len(state.final_answer) > 200:
            quality_score += 2.0
        if "[" in state.final_answer and "]" in state.final_answer:
            quality_score += 3.0
            
    if error_count > 0:
        quality_score -= min(quality_score, error_count * 2.0)
        
    metrics = BenchmarkMetrics(
        run_name=run_name, 
        latency_seconds=latency,
        estimated_cost_usd=total_cost,
        quality_score=quality_score,
        notes=f"Errors: {error_count}"
    )
    return state, metrics
