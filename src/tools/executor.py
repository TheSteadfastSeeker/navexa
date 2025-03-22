from langchain.agents import create_tool_calling_agent, AgentExecutor, AgentType
from langchain_core.prompts import ChatPromptTemplate
from tools import tools
from utils.vector_db_configuration import DefaultVectorStoreConfiguration as VectorStoreConfiguration
from utils.llm_configuration import GoogleLLMConfiguration as LLMConfiguration

vector_store_config = VectorStoreConfiguration()
configuration = LLMConfiguration()
embeddings = configuration.get_embeddings()
llm = configuration.get_llm()
indexes = vector_store_config.get_indexes()
from common import WorkflowState

#################
# EXECUTE_TOOLS #
#################
def execute_tool(state: WorkflowState):
    prompt = ChatPromptTemplate.from_messages([
        ('system', 'You are a smart agent who can execute one of the following utils: utils: {utils}'),
        ("placeholder", "{chat_history}"),
        ('human',"""
                    Please perform the tool invocation based on context and tasks to perform:   
                    
                    context: 
                    {context}
                    
                    details of task to perform: 
                    {steps}
                    
                    query:
                    {query}
                    
                    finally return the result without tags such as ```json or ```.
                """),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent = create_tool_calling_agent(llm=llm,tools=tools,prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    steps = state["steps"][state.get("current_step", 0)]
    context = state.get("output", "")
    print(f"executing Steps: {steps} with Context:{context}")
    result = agent_executor.invoke({"query": state["query"], "utils": tools, "steps": steps, "context": context})
    print(result)
    return result

