# research_manager.py  (rewritten)
import asyncio
from agents import Agent, Runner, trace, gen_trace_id, function_tool
from agents import handoff
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchPlan, WebSearchItem
from writer_agent import writer_agent, ReportData
from clarifier_agent import clarifier_agent, ClarifyingQuestions


# ── Wrap sub-agents as tools ──────────────────────────────────────────────────

@function_tool
async def plan_searches_tool(query_with_clarifications: str) -> str:
    """Plan web searches for a query. Input should include the query and any clarifications."""
    result = await Runner.run(planner_agent, query_with_clarifications)
    plan = result.final_output_as(WebSearchPlan)
    # Serialize so the manager agent can read it
    return "\n".join([f"SEARCH: {s.query} | REASON: {s.reason}" for s in plan.searches])


@function_tool
async def search_web_tool(search_term: str, reason: str) -> str:
    """Perform a single web search and return a summary."""
    input_str = f"Search term: {search_term}\nReason for searching: {reason}"
    try:
        result = await Runner.run(search_agent, input_str)
        return str(result.final_output)
    except Exception as e:
        return f"Search failed: {e}"

report_store = {"markdown": ""}
@function_tool
async def write_report_tool(query: str, search_results: str) -> str:
    """Write a detailed markdown report given the query and concatenated search results."""
    input_str = f"Original query: {query}\nSummarized search results:\n{search_results}"
    result = await Runner.run(writer_agent, input_str)
    report = result.final_output_as(ReportData)
    report_store["markdown"] = report.markdown_report
    return report.markdown_report




# ── Manager Agent ─────────────────────────────────────────────────────────────

MANAGER_INSTRUCTIONS = """You are a deep research orchestrator. When given a query with user clarifications:
1. Call plan_searches_tool with the full context (query + clarifications)
2. Parse the returned search list and call search_web_tool for EACH search in parallel if possible, 
   otherwise sequentially. Collect all results.
3. Call write_report_tool with the original query and all search results concatenated.
4. Return the final markdown report to the user.
Be methodical. Do not skip steps."""

manager_agent = Agent(
    name="ResearchManagerAgent",
    instructions=MANAGER_INSTRUCTIONS,
    tools=[plan_searches_tool, search_web_tool, write_report_tool],
    model="gpt-4o-mini",  # Use a stronger model for orchestration
)


# ── Public interface (used by deep_research.py) ───────────────────────────────

class ResearchManager:

    async def clarify(self, query: str) -> ClarifyingQuestions:
        """Step 1: Get clarifying questions for the UI."""
        result = await Runner.run(clarifier_agent, f"Query: {query}")
        return result.final_output_as(ClarifyingQuestions)

    async def run(self, query: str, clarifications: str):
        """Step 2: Run full research with clarifications, streaming status."""
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            yield "Manager agent starting research..."

            full_input = f"Query: {query}\n\nUser Clarifications:\n{clarifications}"
            result = await Runner.run(manager_agent, full_input)

            yield "Research complete!"
            yield report_store["markdown"]    # The markdown report