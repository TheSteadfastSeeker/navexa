import json
import requests

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain
from pydantic import BaseModel
from tools.vector_db_configuration import FAISSVectorStoreConfiguration as VectorStoreConfiguration
from tools.llm_configuration import GoogleLLMConfiguration as LLMConfiguration

vector_store_config = VectorStoreConfiguration()
configuration = LLMConfiguration()
embeddings = configuration.get_embeddings()
llm = configuration.get_llm()
indexes = vector_store_config.get_indexes()

#########
# tools #
#########
def call_api_endpoint(endpoint: str, params: dict=None):
    url = f"http://127.0.0.1:5000/{endpoint}"
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data from {endpoint}, Status Code: {response.status_code}"}

@chain
def extract_organization_level_data(query: str):
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


@chain
def extract_from_manual(query: str) -> dict[str, str]():
    """Extracts contents from User Manual based on specific keywords."""

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
    context = vector_store_config.get_vector_store_handle(output.equipment_name).similarity_search(output.keywords, k=5)
    return {"equipment_name": output.equipment_name, "context": context, "query": query}


@chain
def summarize(params: dict[str, str]):
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

if __name__ == "__main__":
    equips_str = extract_organization_level_data.invoke("""
                                    Give me list of equipments in the Maritime as a json array of strings.
                                    Always return a valid json response do not send back any extra texts.
                                    
                                    Example: 
                                    Question: 
                                        give me the list of fruits starting with letter 'a'. 
                                    Answer: 
                                        ["apple", "apricot", "apple lemon"]
                                  """).content
    equips:list[str] = json.loads(equips_str)
    class Output(BaseModel):
        name: str
        manufacturer: str
        model_number: str
        characteristics: list[str]
        servicing_details: str

    for equip in equips:
        equip_struct_llm = configuration.get_llm().with_structured_output(Output)
        print(f"{equip}:\n",
            extract_from_manual
            .pipe(summarize)
            .pipe(equip_struct_llm)
            .invoke(f"""
                        Need you to return me the name, model number, manufacturer and characteristics details these equipments: {equip}.
                        Expected format
                        {{
                            "name": "laptop",
                            "model_number": "MacBookPro",
                            "manufacturer":"apple",
                            "characteristics": ["service every 6 months, so that apple can make a lot of money."]
                        }}
                    """))
