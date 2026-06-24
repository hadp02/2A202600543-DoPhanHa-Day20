"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        
        query_lower = query.lower()
        mock_data = [
            SourceDocument(
                title="Introduction to GraphRAG",
                url="https://example.com/graphrag",
                snippet="GraphRAG combines knowledge graphs with Retrieval-Augmented Generation to provide more structured context.",
            ),
            SourceDocument(
                title="State of the Art in Multi-Agent Systems",
                url="https://example.com/mas",
                snippet="Multi-agent systems leverage multiple specialized agents for planning, reasoning, and tool use.",
            ),
            SourceDocument(
                title="Evaluating LLMs with LangGraph",
                url="https://example.com/langgraph-eval",
                snippet="LangGraph offers a robust framework to build cyclic graphs for agent workflows with tracing.",
            ),
        ]
        
        results = [doc for doc in mock_data if any(word in doc.title.lower() or word in doc.snippet.lower() for word in query_lower.split())]
        
        if not results:
            results = mock_data
            
        return results[:max_results]
