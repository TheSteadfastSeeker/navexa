from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from utils.vector_db_configuration import DefaultVectorStoreConfiguration as VectorStoreConfiguration
from utils.llm_configuration import GoogleLLMConfiguration as LLMConfiguration

vector_store_config = VectorStoreConfiguration()
configuration = LLMConfiguration()
embeddings = configuration.get_embeddings()
llm = configuration.get_llm()
indexes = vector_store_config.get_indexes()

#################
# SUMMARIZATION #
#################
@tool
def summarize(context:str, query: str):
    """
    Summary:
        Summarizes the answer in a form which is customer-centric. This utils helps you to create a response which can be served to the user.

    When to use:
        This is usually called just before the final answer is sent back to user as the last step or if the user specifically asks to summarize any particular information.

    Input:
        Give
    Output:
        This should contain the information to summarize.
    """
    summarizer_prompt = ChatPromptTemplate.from_messages(
        [
            ('system', """
                You are a Mechanical Engineer in the Shipping Industry with expertise in Predictive Maintenance.
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
    return (summarizer_prompt | llm).invoke({"context":context, "query": query}).content
