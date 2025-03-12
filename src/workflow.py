from typing import TypedDict, Literal, Union
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
DECIPHER: str = "__decipher__"
DECIDE: str = "__decide__"
API_CALL: str = "__api_call__"
REFER_MANUAL = "__refer_manual__"
CAN_PERFORM_SUMMARIZATION: str = "__can_perform_summarization__"
PERFORM_SUMMARIZATION: str = "__perform_summarization__"
SEND_ALERT: str = "__send_alert__"
DECIDER_RET = Union[API_CALL, REFER_MANUAL, SEND_ALERT, CAN_PERFORM_SUMMARIZATION]
CAN_PERFORM_SUMMARIZATION_RET = Union[PERFORM_SUMMARIZATION, DECIDE]

class Workflow:
    class State(TypedDict):
        next: str
        pass

    def mock(self, state: State):
        pass

    def decider(self, state: State) -> DECIDER_RET:
        self.inspect(state)
        if state["next"] == API_CALL:
            return API_CALL
        elif state["next"] == REFER_MANUAL:
            return REFER_MANUAL
        elif state["next"] == SEND_ALERT:
            return SEND_ALERT
        else:
            return CAN_PERFORM_SUMMARIZATION

    def can_summarize(self, state: State) -> CAN_PERFORM_SUMMARIZATION_RET:
        self.inspect(state)
        if state["next"] == PERFORM_SUMMARIZATION:
            return PERFORM_SUMMARIZATION
        else:
            return DECIDE

    def create_graph(self):
        builder = MessageGraph()
        builder.add_node(DECIPHER, self.mock)
        builder.add_node(DECIDE, self.mock)
        builder.add_node(API_CALL, self.mock)
        builder.add_node(REFER_MANUAL, self.mock)
        builder.add_node(CAN_PERFORM_SUMMARIZATION, self.mock)
        builder.add_node(PERFORM_SUMMARIZATION, self.mock)
        builder.add_node(SEND_ALERT, self.mock)

        builder.set_entry_point(DECIPHER)
        builder.add_edge(DECIPHER, DECIDE)
        builder.add_conditional_edges(DECIDE, self.decider)
        builder.add_edge(API_CALL, CAN_PERFORM_SUMMARIZATION)
        builder.add_edge(REFER_MANUAL, CAN_PERFORM_SUMMARIZATION)
        builder.add_edge(SEND_ALERT, CAN_PERFORM_SUMMARIZATION)
        builder.add_conditional_edges(CAN_PERFORM_SUMMARIZATION, self.can_summarize)
        builder.add_edge(PERFORM_SUMMARIZATION, END)
        graph = builder.compile()
        configuration.draw_graph(graph, PNG_GRAPH)

    def inspect(self, state: State):
        print(state)

if __name__ == "__main__":
    workflow = Workflow()
    workflow.create_graph()

