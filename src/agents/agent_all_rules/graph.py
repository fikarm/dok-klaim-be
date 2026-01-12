# from src.agents.agent_all_rules.tools import tool_node
from src.core.schema import State
from langgraph.graph import END, StateGraph
from langgraph.graph.message import AnyMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    SystemMessage,
    ToolMessage,
)
from langgraph.checkpoint.memory import MemorySaver
from src.agents.agent_all_rules.tools import active_tools


def call_model(state: State):
    # print()
    # print("---")
    # print("state", state)
    # print()

    state_files_as_system_message(state)

    llm_tool = ChatOllama(model="qwen3:latest").bind_tools(active_tools)
    # llm_tool = ChatOllama(model="gemma3:27b").bind_tools(active_tools)
    response = llm_tool.invoke(state["messages"])

    return {"messages": [response]}


def state_files_as_system_message(state: State):
    """Jika ada file yang diupload oleh user, maka buat system message yang berisi list file tersebut."""

    list_file = "\n".join(state["files"])
    systemMessage = SystemMessage(
        f"Berikut adalah file yang diunggah oleh user. \n{list_file}"
    )
    humanMessage = state["messages"].pop()

    state["messages"].append(systemMessage)
    state["messages"].append(humanMessage)


def uploaded_files_as_system_message(messages: list[AnyMessage]):
    """Jika ada file yang diupload oleh user, maka buat system message yang berisi list file tersebut."""

    humanMessage = messages[-1]  # message terakhir harusnya humanMessage
    if "files" in humanMessage.additional_kwargs:
        list_file = "\n".join(
            [file["filepath"] for file in humanMessage.additional_kwargs["files"]]
        )
        systemMessage = SystemMessage(
            f"Berikut adalah file yang diunggah oleh user. \n{list_file}"
        )
        humanMessage = messages.pop()

        messages.append(systemMessage)
        messages.append(humanMessage)


def should_continue(state: State) -> str:
    last_message = state["messages"][-1]

    # print("should_continue", last_message)

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    if isinstance(last_message, AIMessageChunk) and last_message.tool_calls:
        return "tools"
    return END


def generate(state: State):
    tool_messages = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, ToolMessage):
            # if msg.name == "cek_kelengkapan_berkas_klaim_bpjs":
            #     return {"messages": [AIMessage(msg.content)]}
            tool_messages = msg.content
            break

    # print("tool_messages:", tool_messages)

    systemMessage = SystemMessage(
        f"Gunakan konteks berikut ini untuk menjawab pertanyaan user.\n\n{tool_messages}"
        # f"Gunakan konteks berikut ini untuk menjawab pertanyaan user.\n\n{tool_messages}\n"
        # "Jawablah dengan Bahasa Indonesia."
    )

    conversation = [
        msg
        for msg in state["messages"]
        if msg.type in ("human", "system") or (msg.type == "ai" and not msg.tool_calls)
    ]

    llm = ChatOllama(model="gemma3:12b")
    response = llm.invoke([systemMessage] + conversation)

    # return {
    #     "messages": [f"Hasil cek: \n```json\n{tool_messages}\n```\n\n response.content"]
    # }
    return {
        "messages": [
            response
            # AIMessage(
            #     f"Di balik layar: \n```md\n{tool_messages}\n```\n\nResponse AI:\n\n{response.content}"
            # )
        ]
    }
    # return {"messages": [f"Hasil cek: \n{tool_messages}\n\n {response.content}"]}


graph_builder = StateGraph(State)


graph_builder.add_node("agent", call_model)
graph_builder.add_node("tools", ToolNode(active_tools))
graph_builder.add_node("generate", generate)


graph_builder.set_entry_point("agent")
graph_builder.add_conditional_edges(
    "agent", tools_condition, {END: END, "tools": "tools"}
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)
# graph_builder.add_edge("agent", END)


memory = MemorySaver()
agent_all_rules = graph_builder.compile(checkpointer=memory)
