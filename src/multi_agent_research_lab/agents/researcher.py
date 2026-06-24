"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"
    
    def __init__(self) -> None:
        self.search_client = SearchClient()
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        
        query = state.request.query
        max_sources = state.request.max_sources
        sources = self.search_client.search(query=query, max_results=max_sources)
        state.sources.extend(sources)
        
        sources_text = "\n".join(
            [f"- [{i+1}] {s.title} ({s.url}): {s.snippet}" for i, s in enumerate(sources)]
        )
        system_prompt = (
            "You are a professional research agent. Summarize the provided sources "
            "into clear, concise research notes. Always include citations in the format [number]."
        )
        user_prompt = f"Query: {query}\n\nSources:\n{sources_text}"
        
        response = self.llm_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        state.research_notes = response.content
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=response.content,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "sources_found": len(sources),
                }
            )
        )
        state.add_trace_event("researcher_complete", {"sources_found": len(sources)})
        return state
