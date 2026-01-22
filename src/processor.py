import os
from src.logger import logger
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class MedicalDocumentProcessor:
    """
    Handles the ingestion pipeline: Loading PDFs and splitting them 
    into optimized chunks for the Vector Database.
    """
    def __init__(self, data_path: str = "data/"):
        self.data_path = data_path

    def process_documents(self):
        """
        Loads PDF files from the data directory and splits them into chunks.
        """
        logger.info(f"Starting document processing from directory: {self.data_path}")
        
        try:
            # 1. Load PDF Documents
            if not os.path.exists(self.data_path):
                logger.error(f"Data directory not found: {self.data_path}")
                return []

            loader = PyPDFDirectoryLoader(self.data_path)
            raw_docs = loader.load()
            
            logger.info(f"Loaded {len(raw_docs)} raw pages from PDF files.")

            # 2. Split Documents into Chunks
            # Chunk size 1000 with 100 overlap is ideal for medical context retention
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
                add_start_index=True
            )
            
            final_chunks = text_splitter.split_documents(raw_docs)
            
            logger.info(f"Document splitting complete. Total chunks created: {len(final_chunks)}")
            print(f"✅ Processed {len(raw_docs)} pages into {len(final_chunks)} chunks.")
            
            return final_chunks

        except Exception as e:
            logger.error(f"Document Processing Error: {str(e)}", exc_info=True)
            return []

if __name__ == "__main__":
    processor = MedicalDocumentProcessor()
    processor.process_documents()