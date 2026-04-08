# planner_agent.py  (updated)
from pydantic import BaseModel, Field
from agents import Agent

HOW_MANY_SEARCHES = 5

INSTRUCTIONS = f"""You are a helpful research assistant. Given a query AND user clarifications, 
come up with {HOW_MANY_SEARCHES} web search terms that are specifically tuned to the user's chosen 
focus areas. Use the clarifications to narrow scope, depth, and angle of searches."""

class WebSearchItem(BaseModel):
    reason: str = Field(description="Why this search is important given the clarifications.")
    query: str = Field(description="The search term to use.")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="Web searches tuned to the clarified query.")

planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)