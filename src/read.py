from typing import TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain
from pydantic import BaseModel

from tools.vector_db_configuration import PineconeVectorStoreConfiguration as VectorStoreConfiguration
from tools.llm_configuration import GoogleLLMConfiguration as LLMConfiguration
vector_store_config = VectorStoreConfiguration()

if __name__ == "__main__":
    configuration = LLMConfiguration()
    embeddings = configuration.get_embeddings()
    llm = configuration.get_llm()
    indexes = vector_store_config.get_indexes()

    @chain
    def manual_extract(query: str) -> dict[str, str] ():
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
        print(f"Found: {output}")
        context = vector_store_config.get_vector_store_handle(output.equipment_name).similarity_search(output.keywords, k=5)
        return {"context": context, "query": query}

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

                Context: Entropy is a measure of disorder, uncertainty, or randomness in a system. In thermodynamics, it represents the level of chaos within a physical system, with higher entropy indicating more disorder and less available energy. In information theory, entropy quantifies the unpredictability of information, where higher entropy means the information is more unpredictable or random. This concept is central to understanding processes like energy transfer and data compression, and it also plays a key role in algorithms and machine learning, such as decision trees, to measure the uncertainty in datasets.
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

    print((manual_extract|summarize).invoke("explain in layman terms about WHRS in equipment bnw 6s90me?"))
