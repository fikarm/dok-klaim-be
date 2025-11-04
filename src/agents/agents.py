from dataclasses import dataclass
from langgraph.graph.state import CompiledStateGraph
from src.agents.agent_rule_evaluator.graph import agent_rule_evaluator

AgentGraph = CompiledStateGraph


@dataclass
class Agent:
    description: str
    graph_like: CompiledStateGraph


agents: dict[str, Agent] = {
    "agent_rule_evaluator": Agent(
        description="Evaluasi satu rule", graph_like=agent_rule_evaluator
    ),
}


def get_agent(agent_id: str) -> AgentGraph:
    """Get an agent graph, loading lazy agents if needed."""
    return agents[agent_id].graph_like
