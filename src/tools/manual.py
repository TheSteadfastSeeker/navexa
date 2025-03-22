from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

from common import Output
from utils.vector_db_configuration import DefaultVectorStoreConfiguration as VectorStoreConfiguration
from utils.llm_configuration import GoogleLLMConfiguration as LLMConfiguration

vector_store_config = VectorStoreConfiguration()
configuration = LLMConfiguration()
embeddings = configuration.get_embeddings()
llm = configuration.get_llm()
indexes = vector_store_config.get_indexes()

###########################
# USER MANUAL INTEGRATION #
###########################
@tool
def extract_from_manual(query: str) -> dict[str, str]():
    """
    Summary:
        User Manual has details about a specific equipment and components of machinery used in the industry.

    When to use:
        This method should be invoked when user query asks any specific information about a machinery, equipments and components.

    Input:
        To invoke this you "must" provide the name of the equipment or component.

    Output:
        Will give answer to your question to your query based on information from user manual.
    """
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
    print(f"searching in {indexes} \n query: {query}")
    output: Output = (search_keywords_prompt | llm_struct_output).invoke({"equipments": indexes, "query": query})
    print(f"Found.. {output}")
    context = "\n\n\n".join([doc.page_content for doc in vector_store_config.get_vector_store_handle(output.equipment_name).similarity_search(output.keywords, k=5)])
    return {"equipment_name": output.equipment_name, "context": context, "query": query}
