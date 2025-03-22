from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate
from tools import tools
from utils.vector_db_configuration import DefaultVectorStoreConfiguration as VectorStoreConfiguration
from utils.llm_configuration import GoogleLLMConfiguration as LLMConfiguration

vector_store_config = VectorStoreConfiguration()
configuration = LLMConfiguration()
embeddings = configuration.get_embeddings()
llm = configuration.get_llm()
indexes = vector_store_config.get_indexes()
from common import WorkflowState, Steps

########################
# multi-query rewrite  #
########################
def multi_query_rewrite(state: WorkflowState) -> Dict[str, List[Steps]]:
    """Rewrites the user query"""
    tool_bound_llm = configuration.get_llm()
    tool_bound_llm = tool_bound_llm.bind_tools(tools)
    tool_bound_llm = tool_bound_llm.with_structured_output(Steps)

    summarizer_prompt = ChatPromptTemplate.from_messages(
        [
            ('system', """
                    You are a Technical Customer Service Executive who is able to split the user query into logical  steps to answer the question based on following rules.
                    you have the following utils at your disposal {utils}. 
                    
                    
                    Your Task:
                    Your task is to split the user query into a series of steps such that the utils can be used in a particular order. 
                    You must understand the description of each tool then arrange it as a chain. 
                    The output of one tool will become the context to the next if it expects a context.
                    Hence your output is a series of steps one step to call one tool at a time.
                                      
                                      
                    If the question outside this given context or if you are not sure of the answer, directly call the summarize step.
                    Answer should be in json format. Following is an example of the output:
                    Question 1.:
                    I want to get the name, model number and manufacturer of all the equipments of Company Cochin Shipping Inc.
                    
                    Answer:
                    {{
                        "query": "I want to get the name, model number and manufacturer of all the equipments of Company Cochin Shipping Inc."
                        "steps": [
                            {{
                                "order": 1,
                                "tool": "extract_organization_level_data",
                                "reason_it_was_chosen": "first have to call the organization level data to get the organization and the list of equipments.
                            }},
                            {{
                                "order": 2,
                                "tool": "extract_from_manual",
                                "reason_it_was_chosen": "now that I have the equipments I have to extract the information from the manuals.
                            }},
                            {{
                                "order": 3,
                                "tool": "summarize",
                                "reason_it_was_chosen": "now I have to summarize the information.
                            }}
                        ]
                    }} 
                    
                    
                    
                    Question 2.:
                    I want to get the description of CAT C-32
                    
                    Answer:
                    {{
                        "query": "I want to get the name, model number and manufacturer of all the equipments of Company Cochin Shipping Inc."
                        "steps": [
                            {{
                                "order": 1,
                                "tool": "extract_from_manual",
                                "reason_it_was_chosen": "This question is equipment specific and has nothing to do with Organization. 
                            }},
                            {{
                                "order": 2,
                                "tool": "summarize",
                                "reason_it_was_chosen": "now I have to summarize the information.
                            }}
                        ]
                    }} 
                    """),
            ('human', "Please answer my query {query}")
        ]
    )
    steps = (summarizer_prompt | tool_bound_llm).invoke({"utils": tools, **state}).steps
    return {"steps": steps}
