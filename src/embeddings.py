import os
from src.logger import logger
from langchain_huggingface import HuggingFaceEmbeddings

class MedicalEmbeddingManager:
    """
    Manages the initialization of the HuggingFace embedding model 
    used for clinical document vectorization.
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.embeddings = None

    def get_embeddings(self):
        """
        Initializes and returns the embedding model instance.
        """
        try:
            logger.info(f"Initializing Embedding Engine: {self.model_name}")
            
            # Loading the model
            self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
            
            logger.info("Embedding model loaded successfully.")
            print(f"✅ Embedding Model '{self.model_name}' loaded successfully.")
            return self.embeddings
            
        except Exception as e:
            logger.error(f"Failed to load Embedding Model: {str(e)}", exc_info=True)
            raise e

if __name__ == "__main__":
    manager = MedicalEmbeddingManager()
    manager.get_embeddings()