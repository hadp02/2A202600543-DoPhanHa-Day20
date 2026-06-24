"""LangGraph workflow skeleton."""

from typing import Any

from langgraph.graph import END, StateGraph

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.critic import CriticAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.schemas import AgentName
from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph."""

    def __init__(self) -> None:
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.critic = CriticAgent()
        self.app = self.build()

    def build(self) -> Any:
        """Create a LangGraph graph."""
        workflow = StateGraph(ResearchState)
        
        workflow.add_node(AgentName.SUPERVISOR, self.supervisor.run)
        workflow.add_node(AgentName.RESEARCHER, self.researcher.run)
        workflow.add_node(AgentName.ANALYST, self.analyst.run)
        workflow.add_node(AgentName.WRITER, self.writer.run)
        workflow.add_node(AgentName.CRITIC, self.critic.run)
        
        workflow.add_edge(AgentName.RESEARCHER, AgentName.SUPERVISOR)
        workflow.add_edge(AgentName.ANALYST, AgentName.SUPERVISOR)
        workflow.add_edge(AgentName.WRITER, AgentName.CRITIC)
        workflow.add_edge(AgentName.CRITIC, AgentName.SUPERVISOR)
        
        def router(state: ResearchState) -> str:
            if not state.route_history:
                return END
            next_agent = state.route_history[-1]
            if next_agent == "done":
                return END
            return next_agent
            
        workflow.add_conditional_edges(
            AgentName.SUPERVISOR,
            router,
            {
                AgentName.RESEARCHER: AgentName.RESEARCHER,
                AgentName.ANALYST: AgentName.ANALYST,
                AgentName.WRITER: AgentName.WRITER,
                END: END
            }
        )
        
        workflow.set_entry_point(AgentName.SUPERVISOR)
        return workflow.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        from typing import cast
        final_state = self.app.invoke(state)
        if isinstance(final_state, dict):
            return ResearchState.model_validate(final_state)
        return cast(ResearchState, final_state)
