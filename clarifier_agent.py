# clarifier_agent.py
from pydantic import BaseModel, Field
from agents import Agent

class ClarifyingOption(BaseModel):
    label: str = Field(description="Short option label, e.g. 'Beginner', 'Technical deep-dive'")
    value: str = Field(description="What this option means for the research direction")

class ClarifyingQuestion(BaseModel):
    question: str = Field(description="The clarifying question to ask the user")
    options: list[ClarifyingOption] = Field(description="3-4 options the user can pick from")

class ClarifyingQuestions(BaseModel):
    questions: list[ClarifyingQuestion] = Field(description="Exactly 3 clarifying questions")

INSTRUCTIONS = """You are a research scoping assistant. Given a user's research query, generate exactly 3 
clarifying questions that will help focus and tune the research. Each question must have 3-4 concrete 
options the user can select from. Think about: audience/depth level, time scope, specific angle or 
subtopic, format preference. Make options meaningfully distinct."""

clarifier_agent = Agent(
    name="ClarifierAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ClarifyingQuestions,
)