"""Supervisor / router skeleton."""

import os

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        
        max_iterations = int(os.environ.get("MAX_ITERATIONS", "6"))
        if state.iteration >= max_iterations:
            next_agent = "done"
        else:
            if not state.research_notes:
                next_agent = AgentName.RESEARCHER
            elif not state.analysis_notes:
                next_agent = AgentName.ANALYST
            elif not state.final_answer:
                next_agent = AgentName.WRITER
            else:
                next_agent = "done"
        
        state.record_route(next_agent)
        state.add_trace_event("supervisor_decision", {"next": next_agent, "iteration": state.iteration})
        return state
