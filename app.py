# deep_research.py  (updated)
import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager

load_dotenv(override=True)

manager = ResearchManager()

# State to hold questions between steps
_questions_state = []


async def get_clarifications(query: str):
    """Fetch clarifying questions and render them as a readable string for display."""
    cqs = await manager.clarify(query)
    global _questions_state
    _questions_state = cqs.questions

    display = ""
    for i, q in enumerate(_questions_state, 1):
        display += f"**Q{i}: {q.question}**\n"
        for j, opt in enumerate(q.options):
            display += f"  {j+1}. {opt.label} — {opt.value}\n"
        display += "\n"
    return display


def build_clarifications_text(q1_choice: str, q2_choice: str, q3_choice: str) -> str:
    """Map user dropdown selections back to clarification text."""
    lines = []
    for i, (q, choice) in enumerate(
        zip(_questions_state, [q1_choice, q2_choice, q3_choice])
    ):
        matched = next((o for o in q.options if o.label == choice), None)
        if matched:
            lines.append(f"- {q.question}: {matched.value}")
    return "\n".join(lines)


async def run_research(query: str, q1: str, q2: str, q3: str):
    if not query or not query.strip():
        yield "⚠️ Please enter a research topic first."
        return
    clarifications = build_clarifications_text(q1, q2, q3)
    async for chunk in manager.run(query, clarifications):
        yield chunk


def get_option_labels(question_index: int) -> list[str]:
    if question_index < len(_questions_state):
        return [o.label for o in _questions_state[question_index].options]
    return ["Option A", "Option B", "Option C"]


with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# 🔬 Deep Research")

    query_textbox = gr.Textbox(label="What topic would you like to research?")
    clarify_button = gr.Button("Get Clarifying Questions", variant="secondary")
    clarifications_display = gr.Markdown(label="Clarifying Questions")

    with gr.Row():
        q1_dropdown = gr.Dropdown(label="Answer Q1", choices=[], interactive=True)
        q2_dropdown = gr.Dropdown(label="Answer Q2", choices=[], interactive=True)
        q3_dropdown = gr.Dropdown(label="Answer Q3", choices=[], interactive=True)

    run_button = gr.Button("Run Research", variant="primary")
    report = gr.Markdown(label="Research Report",value="")

    async def on_clarify(query):
        if not query or not query.strip():
            return "⚠️ Please enter a research topic first.", gr.update(), gr.update(), gr.update()
        text = await get_clarifications(query)
        q1_opts = get_option_labels(0)
        q2_opts = get_option_labels(1)
        q3_opts = get_option_labels(2)
        return (
            text,
            gr.update(choices=q1_opts, value=q1_opts[0]),
            gr.update(choices=q2_opts, value=q2_opts[0]),
            gr.update(choices=q3_opts, value=q3_opts[0]),
        )

    clarify_button.click(
        fn=on_clarify,
        inputs=query_textbox,
        outputs=[clarifications_display, q1_dropdown, q2_dropdown, q3_dropdown],
    )

    run_button.click(
        fn=run_research,
        inputs=[query_textbox, q1_dropdown, q2_dropdown, q3_dropdown],
        outputs=report,
    )

ui.launch(inbrowser=True)
