import os
from typing import List
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_core.documents import Document

class MedicalLoader:
    """
    Handles loading of medical PDF documents for the HMS RAG Pipeline.
    """
    def __init__(self, directory_path: str):
        self.directory_path = directory_path
        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)
            print(f"📁 Created missing directory: {self.directory_path}")

    def load_documents(self) -> List[Document]:
        """
        Loads all PDFs and adds extra metadata for professional referencing.
        """
        print(f"🚀 Initializing loader for: {self.directory_path}...")
        
        # High-speed PyMuPDF loader
        dir_loader = DirectoryLoader(
            self.directory_path,
            glob="**/*.pdf",
            loader_cls=PyMuPDFLoader,
            show_progress=True,
            use_multithreading=True # Speeds up large document processing
        )

        try:
            documents = dir_loader.load()
            
            # Post-processing: Metadata enhancement
            # Isse AI ko pata chale ga ke exact file name kya hai
            for doc in documents:
                file_full_path = doc.metadata.get("source", "Unknown")
                doc.metadata["file_name"] = os.path.basename(file_full_path)
                
            print(f"✅ Successfully loaded {len(documents)} pages from {self.directory_path}.")
            return documents
            
        except Exception as e:
            print(f"❌ Critical Error during document loading: {str(e)}")
            return []

# Unit Testing (Optional: Only runs if you execute this file directly)
if __name__ == "__main__":
    loader = MedicalLoader("data")
    docs = loader.load_documents()
    if docs:
        print(f"Sample Metadata: {docs[0].metadata}")