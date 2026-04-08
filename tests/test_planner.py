# test_planner.py
import asyncio
from agents import Runner
from planner_agent import planner_agent

async def test():
    input = """Query: AI in healthcare
Clarifications:
- Audience: Medical professionals
- Time scope: Last 2 years  
- Focus: Diagnostics and imaging"""
    result = await Runner.run(planner_agent, input)
    for s in result.final_output.searches:
        print(f"- {s.query} ({s.reason})")

asyncio.run(test())