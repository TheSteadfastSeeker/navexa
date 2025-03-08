import os

from langchain_ollama import ChatOllama
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.graph.graph import CompiledGraph

load_dotenv()

class LLMConfiguration:
    def get_llm(self, **configuration):
        pass

    def get_embeddings(self):
        pass

    def draw_graph(self, graph: CompiledGraph, filename_without_extension: str):
        graph.get_graph().draw_png(f"misc/{filename_without_extension}.png")


class GoogleLLMConfiguration(LLMConfiguration):
    def __init__(self):
        os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

    def get_llm(self, **configuration):
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", **configuration)

    def get_embeddings(self):
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")


class OllamaLLMConfiguration(LLMConfiguration):
    def get_llm(self, **configuration):
        return ChatOllama(model="llama3.2:1b", **configuration)

class DefaultLLMConfiguration(GoogleLLMConfiguration):
    pass