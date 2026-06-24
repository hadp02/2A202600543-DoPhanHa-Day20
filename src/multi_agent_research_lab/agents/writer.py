"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"
    
    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        
        system_prompt = (
            "You are an expert technical writer. Synthesize the provided research notes "
            f"and analysis into a comprehensive, clear final answer for the audience: {state.request.audience}. "
            "Always include citations or source references."
        )
        user_prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}\n\nAnalysis:\n{state.analysis_notes}"
        
        response = self.llm_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        state.final_answer = response.content
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=response.content,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                }
            )
        )
        state.add_trace_event("writer_complete", {})
        return state
