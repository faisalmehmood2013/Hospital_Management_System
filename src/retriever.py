import os
from src.logger import logger

class MedicalRAGRetriever:
    """
    Handles retrieval of relevant medical context from the Pinecone vector database.
    """
    def __init__(self, vectorstore):
        # Vectorstore object is initialized and passed from app.py
        self.vectorstore = vectorstore

    def retrieve(self, query: str, top_k: int = 3):
        """
        Retrieves the top K most relevant medical document chunks based on user query.
        """
        logger.info(f"Initiating retrieval for query: '{query}'")
        
        try:
            # 1. Validation: Ensure vectorstore is properly connected
            if self.vectorstore is None:
                logger.error("Retrieval Failed: VectorStore object is None. Verify Pinecone connection.")
                return []

            # 2. Vector Search: Perform similarity search with confidence scores
            # Higher scores indicate better document relevance
            results = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            if not results:
                logger.warning(f"No matching medical documents found for: '{query}'")
                return []

            # 3. Data Processing
            retrieved_docs = []
            for doc, score in results:
                # Optional: Filter by score threshold if needed (e.g., score > 0.1)
                logger.info(f"Matched chunk with relevance score: {score}")
                retrieved_docs.append(doc)
            
            logger.info(f"Successfully retrieved {len(retrieved_docs)} medical context chunks.")
            return retrieved_docs

        except Exception as e:
            logger.error(f"Critical Retrieval Error: {str(e)}", exc_info=True)
            return []

# --- Manual Debugging Block ---
if __name__ == "__main__":
    print("Direct execution disabled. Please run via app.py or 'python -m src.retriever'")