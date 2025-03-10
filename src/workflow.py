from typing import TypedDict, Literal
from langgraph.constants import END
from langgraph.graph import MessageGraph, Graph
from tools.vector_db_configuration import DefaultVectorStoreConfiguration as VectorStoreConfiguration
from tools.llm_configuration import GoogleLLMConfiguration as LLMConfiguration

vector_store_config = VectorStoreConfiguration()
configuration = LLMConfiguration()
embeddings = configuration.get_embeddings()
llm = configuration.get_llm()
indexes = vector_store_config.get_indexes()

PNG_GRAPH = "output"

############
# Workflow #
############
class Workflow:
    class State(TypedDict):
        next: str
        pass

    def mock(self, state: State):
        pass

    def decider(self, state: State) -> Literal["__api_call__", "__refer_manual__", "__send_alert__", "__can_perform_summarization__"]:
        self.inspect(state)
        if state["next"] == "__api_call__":
            return "__api_call__"
        elif state["next"] == "__refer_manual__":
            return "__refer_manual__"
        elif state["next"] == "__send_alert__":
            return "__send_alert__"
        else:
            return "__can_perform_summarization__"

    def can_summarize(self, state: State) -> Literal["__perform_summarization__", "__decide__"]:
        self.inspect(state)
        if state["next"] == "__perform_summarization__":
            return "__perform_summarization__"
        else:
            return "__decide__"

    def create_graph(self):
        builder = MessageGraph()
        builder.add_node("__decipher__", self.mock)
        builder.add_node("__decide__", self.mock)
        builder.add_node("__api_call__", self.mock)
        builder.add_node("__refer_manual__", self.mock)
        builder.add_node("__can_perform_summarization__", self.mock)
        builder.add_node("__perform_summarization__", self.mock)
        builder.add_node("__send_alert__", self.mock)

        builder.set_entry_point("__decipher__")
        builder.add_edge("__decipher__", "__decide__")
        builder.add_conditional_edges("__decide__", self.decider)
        builder.add_edge("__api_call__", "__can_perform_summarization__")
        builder.add_edge("__refer_manual__", "__can_perform_summarization__")
        builder.add_edge("__send_alert__", "__can_perform_summarization__")
        builder.add_conditional_edges("__can_perform_summarization__", self.can_summarize)
        builder.add_edge("__perform_summarization__", END)
        graph = builder.compile()
        configuration.draw_graph(graph, PNG_GRAPH)

    def inspect(self, state: State):
        print(state)

if __name__ == "__main__":
    workflow = Workflow()
    workflow.create_graph()

