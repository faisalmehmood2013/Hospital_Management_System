import os
from dotenv import load_dotenv
from pinecone import Pinecone as PineconeClient
from langchain_pinecone import PineconeVectorStore

load_dotenv()

class MedicalVectorManager:
    def __init__(self, embedding_model):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        self.embeddings = embedding_model
        
        try:
            # Direct Connection
            self.pc = PineconeClient(api_key=self.api_key)
            self.index = self.pc.Index(self.index_name)
            
            # Langchain setup
            self.vectorstore = PineconeVectorStore(
                index_name=self.index_name,
                embedding=self.embeddings,
                pinecone_api_key=self.api_key
            )
            
            # Check if data exists
            stats = self.index.describe_index_stats()
            print(f"✅ Connected to Pinecone Index: {self.index_name}")
            print(f"📊 Total Vectors in Database: {stats['total_vector_count']}")
            
        except Exception as e:
            print(f"❌ Connection Failed: {str(e)}")
            self.vectorstore = None

    def get_vectorstore_object(self):
        return self.vectorstore

# Isolated Testing Block (FIXED)
if __name__ == "__main__":
    # Jab direct run karein to local import use karein
    try:
        import sys
        sys.path.append(os.getcwd()) # Current directory ko path mein add karein
        from embeddings import MedicalEmbeddingManager 
        
        embed_manager = MedicalEmbeddingManager()
        vm = MedicalVectorManager(embedding_model=embed_manager.get_embeddings())
    except ImportError:
        print("Run this from the main project folder using: python src/vector_store.py")