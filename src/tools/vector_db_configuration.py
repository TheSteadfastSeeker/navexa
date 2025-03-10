import os

from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores import Pinecone as LangChainPinecone, PGVector
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from pinecone import Pinecone, ServerlessSpec
from tools.llm_configuration import DefaultLLMConfiguration as LLMConfiguration
from langchain_community.vectorstores import FAISS
import faiss
configuration = LLMConfiguration()
import psycopg2

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = "us-east-1"

class VectorStoreConfiguration:
    def get_vector_store_embedding_model(self) -> Embeddings:
        return configuration.get_embeddings()

    def get_indexes(self):
        pass

    def get_vector_store_handle(self, index_name: str) -> VectorStore:
        pass

class PineconeVectorStoreConfiguration(VectorStoreConfiguration):
    def __init__(self):
        self.pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

    def get_vector_store_embedding_model(self) -> Embeddings:
        return super().get_vector_store_embedding_model()

    def get_indexes(self):
        return self.pc.list_indexes()

    def get_vector_store_handle(self, index_name: str) -> VectorStore:
        if index_name not in [index_info["name"] for index_info in self.pc.list_indexes()]:
            print(f"Index '{index_name}' not found. Creating a new index...")
            self.pc.create_index(
                name=index_name,
                spec=ServerlessSpec(
                    cloud="aws",
                    region=PINECONE_ENVIRONMENT
                ),
                dimension=768,
                metric="cosine"
            )

        index = self.pc.Index(name=index_name)
        vector_store = LangChainPinecone(
            index=index,
            embedding=self.get_vector_store_embedding_model(),
            text_key="text"
        )
        return vector_store


class FAISSVectorStoreConfiguration(VectorStoreConfiguration):
    def __init__(self):
        self.index = None
        self.texts = []
        self.indexes = {}

    def get_vector_store_embedding_model(self) -> Embeddings:
        return super().get_vector_store_embedding_model()

    def get_indexes(self):
        if not self.indexes:
            print("No indexes found.")
            return []
        return list(self.indexes.keys())

    def get_vector_store_handle(self, index_name: str) -> VectorStore:
        if self.index is None:
            print(f"Initializing in-memory vector store for '{index_name}'...")
            dimension = 768
            self.index = faiss.IndexFlatL2(dimension)

        vector_store = FAISS(
            index=self.index,
            embedding_function=self.get_vector_store_embedding_model(),
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        self.indexes[index_name] = self.index
        return vector_store


class PGVectorStoreConfiguration(VectorStoreConfiguration):
    def __init__(self, connection_string=None):
        self.connection_string = connection_string or f"postgresql://navexa_user:navexa_password@localhost:5432/maritime_predictive_maintenance"
        self.indexes = {}

    def get_vector_store_embedding_model(self) -> Embeddings:
        return super().get_vector_store_embedding_model()

    def get_indexes(self):
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM public.langchain_pg_collection;")
                collections = [row[0] for row in cursor.fetchall()]
        return collections

    def get_vector_store_handle(self, index_name: str) -> VectorStore:
        vector_store = PGVector(
            connection_string=self.connection_string,
            embedding_function=self.get_vector_store_embedding_model(),
            collection_name=index_name
        )
        return vector_store
class DefaultVectorStoreConfiguration(PGVectorStoreConfiguration):
    pass