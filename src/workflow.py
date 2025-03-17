from typing import TypedDict, Union, Literal
from langgraph.constants import END
from langgraph.graph import MessageGraph, StateGraph
from langgraph.graph.graph import CompiledGraph

from state import WorkflowState
from tools.vector_db_configuration import DefaultVectorStoreConfiguration as VectorStoreConfiguration
from tools.llm_configuration import GoogleLLMConfiguration as LLMConfiguration
from utility import multi_query_rewrite, execute_tool

vector_store_config = VectorStoreConfiguration()
configuration = LLMConfiguration()
embeddings = configuration.get_embeddings()
llm = configuration.get_llm()
indexes = vector_store_config.get_indexes()

PNG_GRAPH = "output"
DECIPHER: str = "__decipher__"
DECIDE: str = "__decide__"
ROUTER: str = "__router__"
EXECUTE_STEP: str = "__execute_step__"
API_CALL: str = "__api_call__"
STEP_COUNTER: str = "__step_counter__"
REFER_MANUAL = "__refer_manual__"
CAN_PERFORM_SUMMARIZATION: str = "__can_perform_summarization__"
PERFORM_SUMMARIZATION: str = "__perform_summarization__"
SEND_ALERT: str = "__send_alert__"
DECIDER_RET = Union[API_CALL, REFER_MANUAL, SEND_ALERT, CAN_PERFORM_SUMMARIZATION]
CAN_PERFORM_SUMMARIZATION_RET = Union[PERFORM_SUMMARIZATION, DECIDE]

def execute_step(state: WorkflowState):
    current_step = state.get("current_step", -1) + 1
    execution_result = execute_tool(state)
    return {"current_step": current_step, "output": execution_result}

def perform_route(state: WorkflowState) -> str:
    if state["current_step"] < len(state["steps"]):
        return EXECUTE_STEP
    else:
        return END

class Workflow:
    def create_graph(self) -> CompiledGraph:
        builder = StateGraph(WorkflowState)
        builder.add_node(DECIPHER, multi_query_rewrite)
        builder.add_node(EXECUTE_STEP, execute_step)

        builder.set_entry_point(DECIPHER)
        builder.add_edge(DECIPHER, EXECUTE_STEP)
        builder.add_conditional_edges(EXECUTE_STEP, perform_route)

        graph: CompiledGraph = builder.compile()
        configuration.draw_graph(graph, PNG_GRAPH)
        return graph

if __name__ == "__main__":
    workflow: CompiledGraph = Workflow().create_graph()
    print(workflow.invoke({"user_query": "Give me all the list of equipments and it's 2 unique characteristics for Maritime"}))

    # while query != "exit":
    #     if query != "":
    #         for step in workflow.stream({"query": query}):
    #             print(step)
    #     query = input("Enter your query: ")
    # print("Thanks.")