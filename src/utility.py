from typing import List

import requests
from langchain_core.tools import Tool

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from tools.vector_db_configuration import DefaultVectorStoreConfiguration as VectorStoreConfiguration
from tools.llm_configuration import GoogleLLMConfiguration as LLMConfiguration
vector_store_config = VectorStoreConfiguration()
configuration = LLMConfiguration()
embeddings = configuration.get_embeddings()
llm = configuration.get_llm()
indexes = vector_store_config.get_indexes()

###################
# API INTEGRATION #
###################
def call_api_endpoint(endpoint: str, params: dict=None, host="http://127.0.0.1:5000/"):
    url = f"{host}/{endpoint}"
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data from {endpoint}, Status Code: {response.status_code}"}

def extract_organization_level_data(query: str):
    """
    This tool should be used whenever the query need the organization level information to answer the use query.
    Following are the information that you can get.

    Organization:
    organization_id (integer)
    name (string)
    contact_info (string)
    subscription_level (string)
    type (string)
    fleets (array of Fleet objects)

    Fleet:
    fleet_id (integer)
    name (string)
    description (string)
    type (string)
    vessels (array of Vessel objects)

    Vessel:
    vessel_id (integer)
    name (string)
    type (string)
    build_year (integer)
    classification (string)
    dimensions (string)
    gross_tonnage (string)
    equipment (array of Equipment objects)

    Equipment:
    equipment_id (integer)
    manual_ref (string)
    manufacturer (string)
    model (string)
    specifications (string)
    type (string)
    installation_date (string)
    components (array of Component objects)

    Component:
    component_id (integer)
    name (string)
    serial_number (string)
    manufacturer (string)
    installation_date (string)
    type (string)

    Relationships:
    Organization contains an array of Fleet objects.
    Fleet contains an array of Vessel objects.
    Vessel contains an array of Equipment objects.
    Equipment contains an array of Component objects.

    """
    org_list: str = call_api_endpoint("api/organizations")
    class Organization(BaseModel):
        """Organization under consideration"""
        name: str
        id: int

    org_ext_llm = configuration.get_llm().with_structured_output(Organization)
    org_ext_prompt = ChatPromptTemplate.from_messages([
        ('system',
         """
         You are a helpful Assistant who is able to extract the actual Organization name and the organization id from {org_list} based on user query
         give it to me in the json format.
         Do not include any other text along with the actual json output.
          
         Example of the output format is
         {{
             "name": "microsoft",
             "id": 123
         }}
         """),
        ('human', 'query: {query}')
    ])
    org: Organization = org_ext_prompt.pipe(org_ext_llm).invoke({"query": query, "org_list": org_list})

    org_details = call_api_endpoint(f"api/organization/{org.id}")
    org_details_prompt = ChatPromptTemplate.from_messages([
        ('system',
         """
         You are a helpful Assistant who is answer query based on context: {context}.
         Give exact answers. Do not include text like ```json etc.
         """),
        ('human', 'extract the information based on user query: {query}')
    ])
    return org_details_prompt.pipe(llm).invoke({"context": org_details, "query": query})

###########################
# USER MANUAL INTEGRATION #
###########################
def extract_from_manual(query: str) -> dict[str, str]():
    """ User Manual has details about a specific equipment and components of machinery used in the industry.
        You have access to User Manual Archives. You are able to answer your queries based on information available in the user manual.
    """
    class Output(BaseModel):
        equipment_name: str
        keywords: str

    search_keywords_prompt = ChatPromptTemplate.from_messages(
        [
            ('system', """
                You are a Mechanical Engineer in the Shipping Industry with expertise in Predictive Maintenance.
                You have to find relevant words from user query which will help me search out relevant contents from instruction manual.
                You have to only return me the words as space separated. No other words apart from the search terms must be returned.
                equipment name must be selected from {equipments}

                Example:
                What is the weight and size of the abc engine?
                Answer:
                {{
                    'equipment_name': 'abc-engine',
                    'keywords': 'weight size'
                }}
                """),
            ('human', "Please answer my query {query}")
        ]
    )
    llm_struct_output = configuration.get_llm().with_structured_output(Output)
    output: Output = (search_keywords_prompt | llm_struct_output).invoke({"equipments": indexes, "query": query})
    context = "\n\n\n".join([doc.page_content for doc in vector_store_config.get_vector_store_handle(output.equipment_name).similarity_search(output.keywords, k=5)])
    return {"equipment_name": output.equipment_name, "context": context, "query": query}

#################
# SUMMARIZATION #
#################
def summarize(params: dict[str, str]):
    """Summarizes the answer in a form which is customer centric. This tools helps you to create a response which can be served to the user.
       Call this tool only after you have all the information to answer the user query.
    """
    summarizer_prompt = ChatPromptTemplate.from_messages(
        [
            ('system', """
                You are a Mechanical Engineer in the Shipping Industry with expertise in Predictive Maintanance.
                You have to summarize text for me based on context {context}.
                Directly get to the point, don't include text like The answer to your question is
                Give me the answer in bullet points
                Example: 

                Context: Entropy is a measure of disorder, uncertainty, or randomness in a system. 
                In thermodynamics, it represents the level of chaos within a physical system, with higher entropy indicating more disorder and less available energy. 
                In information theory, entropy quantifies the unpredictability of information, where higher entropy means the information is more unpredictable or random. 
                This concept is central to understanding processes like energy transfer and data compression, and it also plays a key role in algorithms and machine learning, 
                such as decision trees, to measure the uncertainty in datasets.

                Question: What does the document talk about entropy?
                Answer: • Entropy measures disorder or uncertainty in a system.
                        • It reflects unpredictability in both thermodynamics and information theory.
                        • In thermodynamics, it represents the level of chaos and available energy.
                        • In information theory, it quantifies the unpredictability of data or information.
                        • It is important in fields like physics, mathematics, and machine learning.
                """),
            ('human', "Please answer my query {query}")
        ]
    )
    return (summarizer_prompt | llm).invoke(params).content

########################
# multi-query rewrite  #
########################
class Step(BaseModel):
    """Each Tool invocation Step"""
    order: int
    """order in which this step must be performed"""
    tool: str
    reason: str

class Workflow(BaseModel):
    """Query and the list of steps to perform to answer the user query."""
    query: str
    steps: List[Step]

tools = [
    Tool(name="extract_organization_level_data", description="extract_organization_level_data", func=extract_organization_level_data),
    Tool(name="extract_from_manual", description="extract_from_manual", func=extract_from_manual),
    Tool(name="summarize", description="summarize", func=summarize),
]

def multi_query_rewrite(query: str) -> Workflow:
    """Rewrites the user query"""
    tool_bound_llm = configuration.get_llm()
    tool_bound_llm = tool_bound_llm.bind_tools(tools)
    tool_bound_llm = tool_bound_llm.with_structured_output(Workflow)

    summarizer_prompt = ChatPromptTemplate.from_messages(
        [
            ('system', """
                    You are a Technical Customer Service Executive who is able to split the user query into logical  steps to answer the question based on following rules.
                    you have the following tools at your disposal {tools}. Following are the rules:
                    
                    - If there is a extract_organization_level_data step it should be the first one in the list.
                    - If there is a extract_from_manual step, it will come first if no extract_organization_level_data, otherwise after extract_organization_level_data.
                    - The summarize step is always the last step.
                    
                    If the question outside this given context or if you are not sure of the answer, directly call the summarize step.
                    
                    Answer should be in json format. Following is an example of the output:
                    
                    Question 1.:
                    I want to get the name, model number and manufacturer of all the equipments of Company Cochin Shipping Inc.
                    
                    Answer:
                    {{
                        "query": "I want to get the name, model number and manufacturer of all the equipments of Company Cochin Shipping Inc."
                        "steps": [
                            {{
                                "step": "extract_organization_level_data",
                                "reason": "first have to call the organization level data to get the organization and the list of equipments.
                            }},
                            {{
                                "step": "extract_from_manual",
                                "reason": "now that I have the equipments I have to extract the information from the manuals.
                            }},
                            {{
                                "step": "summarize",
                                "reason": "now I have to summarize the information.
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
                                "tool": "extract_from_manual",
                                "reason": "This question is equipment specific and has nothing to do with Organization. 
                            }},
                            {{
                                "tool": "summarize",
                                "reason": "now I have to summarize the information.
                            }}
                        ]
                    }} 
                    """),
            ('human', "Please answer my query {query}")
        ]
    )
    return (summarizer_prompt | tool_bound_llm).invoke({"query": query, "tools": tools})