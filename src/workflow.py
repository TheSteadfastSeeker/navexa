from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph

from common import WorkflowState
from tools.executor import execute_tool
from tools.query_rewrite import multi_query_rewrite
from utils.vector_db_configuration import DefaultVectorStoreConfiguration as VectorStoreConfiguration
from utils.llm_configuration import GoogleLLMConfiguration as LLMConfiguration

vector_store_config = VectorStoreConfiguration()
configuration = LLMConfiguration()
embeddings = configuration.get_embeddings()
llm = configuration.get_llm()
indexes = vector_store_config.get_indexes()

PNG_GRAPH = "output"
DECIPHER: str = "__decipher__"
EXECUTE_STEP: str = "__execute_step__"
SEND_ALERT: str = "__send_alert__"

def execute_step(state: WorkflowState):
    current_step = state.get("current_step", -1) + 1
    execution_result = execute_tool(state)
    return {"current_step": current_step, "output": execution_result}

def perform_route(state: WorkflowState) -> str:
    if state["current_step"] < len(state["steps"])-1:
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
    for c in workflow.invoke({"query": "Give me all the list of equipments and then from the user manual give me 2 characteristics for Maritime"}):
        print(c)
