from src.core.schema import State
from langgraph.graph import END, StateGraph
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from src.agents.agent_rule_evaluator_vector.main import cek_kelengkapan


def agent(state: State):
    try:
        response = cek_kelengkapan(state["files"][0], state["messages"][-1].content)

        if not response:
            raise ValueError("tidak ada response")

        return {"messages": [AIMessage(response)]}
    except Exception as e:
        return {"messages": [str(e)]}


graph_builder = StateGraph(State)
graph_builder.add_node("agent", agent)
graph_builder.set_entry_point("agent")
graph_builder.add_edge("agent", END)


memory = MemorySaver()
agent_rule_evaluator_vector = graph_builder.compile(checkpointer=memory)
