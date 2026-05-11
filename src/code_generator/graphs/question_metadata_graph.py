import json
from pathlib import Path
from typing import List, TypedDict
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph
from pydantic import Field
from src.models import Question, QuestionTypes
from src.utils import save_graph_visualization, to_serializable


# --- External Services ---
from langsmith import Client

model = init_chat_model(
    model="gpt-4o",
    model_provider="openai",
)


client = Client()
base_prompt = client.pull_prompt("base_metadata")
if isinstance(base_prompt, str):
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(base_prompt)
else:
    prompt: ChatPromptTemplate = base_prompt


class QuestionMetaData(BaseModel):
    title: str = Field(..., description="A concise title summarizing the question")
    question_types: List[QuestionTypes] = []
    topics: List[str] = Field(default=[])
    isAdaptive: bool


class State(BaseModel):
    question: Question
    metadata: QuestionMetaData | None = Field(
        default=None,
        description="The metadata to generate",
    )
    isAdaptive: bool | None = Field(
        default=None,
        description="Whether the question is adaptive or not. If the None is passed it will auto generate during metadata generation. ",
    )


def generate_question_metadata(state: State):
    question_text = state.question.question_text

    structured_model = model.with_structured_output(QuestionMetaData)
    messages = prompt.format_prompt(question=question_text).to_messages()

    result = structured_model.invoke(messages)
    metadata = QuestionMetaData.model_validate(result)

    # Override
    if state.isAdaptive is not None:
        metadata.isAdaptive = state.isAdaptive

    return {"metadata": metadata}


workflow = StateGraph(State)
# Define Nodes
workflow.add_node("generate_question_metadata", generate_question_metadata)
# Connect
workflow.add_edge(START, "generate_question_metadata")
workflow.add_edge("generate_question_metadata", END)

# memory = MemorySaver()
# app = workflow.compile(checkpointer=memory)
app = workflow.compile()
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "customer_123"}}
    question = Question(
        question_text="A car is traveling along a straight rode at a constant speed of 100mph for 5 hours calculate the total distance traveled",
        solution_guide=None,
        final_answer=None,
        question_html="",
    )
    input_state: State = State(**{"question": question, "metadata": None})
    result = app.invoke(input_state, config=config)  # type: ignore
    print(result["metadata"])

    # Save output
    output_path = Path(
        r"langgraph_server/gestalt_graphs/code_generator/outputs/metadata"
    )
    save_graph_visualization(app, output_path, filename="graph.png")
    data_path = output_path / "output.json"
    data_path.write_text(json.dumps(to_serializable(result)))
