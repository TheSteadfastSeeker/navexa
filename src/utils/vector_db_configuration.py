import faiss
import psycopg2
from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores import PGVector
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from utils.llm_configuration import DefaultLLMConfiguration as LLMConfiguration
from langchain_community.vectorstores import FAISS

configuration = LLMConfiguration()

class VectorStoreConfiguration:
    def get_vector_store_embedding_model(self) -> Embeddings:
        return configuration.get_embeddings()

    def get_indexes(self):
        pass

    def get_vector_store_handle(self, index_name: str) -> VectorStore:
        pass

class FAISSVectorStoreConfiguration(VectorStoreConfiguration):
    """Use this for speed and small data."""
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
    """Use this for persistent storage"""
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