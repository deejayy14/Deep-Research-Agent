# test_clarifier.py
import asyncio
from agents import Runner
from clarifier_agent import clarifier_agent

async def test():
    result = await Runner.run(clarifier_agent, "Query: AI in healthcare")
    for q in result.final_output.questions:
        print(f"\nQ: {q.question}")
        for opt in q.options:
            print(f"  - {opt.label}: {opt.value}")

asyncio.run(test())