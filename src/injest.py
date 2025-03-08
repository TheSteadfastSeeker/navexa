import os
from PyPDF2 import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from tools.vector_db_configuration import PineconeVectorStoreConfiguration as VectorStoreConfiguration
from tools.llm_configuration import GoogleLLMConfiguration as LLMConfiguration
vector_store_config = VectorStoreConfiguration()


class PDFIngestion:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path

    def ingest_pdfs_to_index(self):
        """
        Ingest all PDF files in the folder into the FAISS index.
        The index is created based on the name of the PDF file.
        """
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".pdf"):
                save_name = filename[0: -4].lower()
                file_path = os.path.join(self.folder_path, filename)
                print(f"Ingesting PDF file: {filename}")
                text = self.extract_text_from_pdf(file_path)
                vector_store = vector_store_config.get_vector_store_handle(save_name)
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=50,
                    length_function=len,
                    is_separator_regex=False,
                )
                docs = text_splitter.create_documents([text])
                vector_store.add_documents(docs)
                print(f"Successfully ingested '{filename}' into the index.")

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file.
        """
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text

if __name__ == "__main__":
    pdf_folder = "../docs/manuals/equipment"
    pdf_ingestion = PDFIngestion(pdf_folder)
    pdf_ingestion.ingest_pdfs_to_index()

    configuration = LLMConfiguration()
    embeddings = configuration.get_embeddings()
    llm = configuration.get_embeddings()
    print(vector_store_config.get_vector_store_handle("caterpillar-c32").similarity_search("service", k=5))
