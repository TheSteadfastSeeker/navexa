import requests
from langchain_core.tools import tool

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from utils.vector_db_configuration import DefaultVectorStoreConfiguration as VectorStoreConfiguration
from utils.llm_configuration import GoogleLLMConfiguration as LLMConfiguration
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

@tool
def extract_organization_level_data(query: str):
    """
    Summary:
        This tool should be used whenever the query need the organization level information to answer the use query.
        To invoke this tool the query must contain the name of the organization for which the data must be extracted.

    When to use:
        This utils is to used whenever the next stage requires the organization level data or other pieces of information required to do its tasks.
        Following are the list of information this api would be able to provide:
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


    Input
        The input Query "must" contain the name of the organization required to look up the query.

    Output:
        The output will contain the full set of information for a particular organization
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
