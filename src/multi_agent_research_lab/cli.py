"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline."""

    _init()
    
    def single_agent_runner(q: str) -> ResearchState:
        from multi_agent_research_lab.core.schemas import AgentName, AgentResult
        from multi_agent_research_lab.services.llm_client import LLMClient
        llm = LLMClient()
        st = ResearchState(request=ResearchQuery(query=q))
        system_prompt = (
            "You are a single research agent. Answer the query directly, "
            "acting as a researcher, analyst and writer. Provide a 500-word "
            "summary with citations."
        )
        user_prompt = f"Query: {q}"
        resp = llm.complete(system_prompt, user_prompt)
        st.final_answer = resp.content
        st.agent_results.append(AgentResult(
            agent=AgentName.WRITER,
            content=resp.content,
            metadata={"input_tokens": resp.input_tokens, "output_tokens": resp.output_tokens, "cost_usd": resp.cost_usd}
        ))
        return st

    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    state, metrics = run_benchmark("baseline", query, single_agent_runner)
    
    import os

    from multi_agent_research_lab.evaluation.report import render_markdown_report
    os.makedirs("reports", exist_ok=True)
    with open("reports/benchmark_report.md", "a") as f:
        f.write(render_markdown_report([metrics]))
    
    console.print(Panel.fit(state.final_answer or "", title="Single-Agent Baseline"))
    console.print(metrics.model_dump_json(indent=2))

@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    
    def multi_agent_runner(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        try:
            return workflow.run(state)
        except StudentTodoError as exc:
            console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
            raise typer.Exit(code=2) from exc

    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    state, metrics = run_benchmark("multi-agent", query, multi_agent_runner)
    
    import os

    from multi_agent_research_lab.evaluation.report import render_markdown_report
    os.makedirs("reports", exist_ok=True)
    with open("reports/benchmark_report.md", "a") as f:
        f.write(render_markdown_report([metrics]))
        
    console.print(Panel.fit(state.final_answer or "", title="Multi-Agent Final Answer"))
    console.print(metrics.model_dump_json(indent=2))

if __name__ == "__main__":
    app()
