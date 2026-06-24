"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"
    
    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""
        
        system_prompt = "You are a critic. Review the research notes, analysis, and final answer. Fact-check the final answer against the notes and flag any hallucinations or lack of citations. Output 'PASS' if good, or detail issues if not."
        user_prompt = f"Research Notes:\n{state.research_notes}\n\nAnalysis:\n{state.analysis_notes}\n\nFinal Answer:\n{state.final_answer}"
        
        response = self.llm_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=response.content,
                metadata={"input_tokens": response.input_tokens, "output_tokens": response.output_tokens}
            )
        )
        if "PASS" not in response.content.upper():
            state.errors.append("Critic flagged issues: " + response.content)
            
        state.add_trace_event("critic_complete", {"passed": "PASS" in response.content.upper()})
        return state
