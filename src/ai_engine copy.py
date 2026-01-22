import os
from dotenv import load_dotenv
from src.logger import logger
from langchain_groq import ChatGroq # Gemini ki jagah Groq use hoga
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

load_dotenv()

class MedicalAIEngine:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            logger.error("GROQ_API_KEY is missing in environment variables.")
            raise ValueError("❌ GROQ_API_KEY is missing.")

        try:
            # Groq is much faster and currently has a generous free tier
            self.llm = ChatGroq(
                groq_api_key=self.api_key,
                model_name=model_name,
                temperature=0.1,
                max_tokens=1024
            )
            logger.info(f"Groq AI Engine Online: {model_name}")
            print(f"✅ Groq Professional AI Online: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq: {str(e)}")
            raise e

    def generate_response(self, query: str, retrieved_docs: list) -> str:
        logger.info(f"Generating Groq response for: '{query}'")
        
        context_parts = []
        for doc in retrieved_docs:
            source = os.path.basename(doc.metadata.get('source', 'Ref'))
            page = doc.metadata.get('page', 'N/A')
            context_parts.append(f"SOURCE [{source}, Page {page}]:\n{doc.page_content}")
        
        context_text = "\n\n".join(context_parts)

        template = """
        SYSTEM ROLE:
        You are a Specialized Medical Document Assistant. Your knowledge is strictly limited 
        to the provided context.

        STRICT RULES:
        1. ONLY answer using the information found in the PROVIDED CONTEXT.
        2. If the answer is NOT present in the context, do not use your own knowledge. 
        3. In case of missing information, your ONLY response should be: 
           "This information is not available in the provided medical records. Please consult a specialist."
        4. Format the output professionally with bold headings and bullet points.

        CONTEXT: 
        {context}

        QUESTION: 
        {question}

        STRICT MEDICAL ANSWER:
        """
        
        try:
            prompt_wrapper = PromptTemplate.from_template(template)
            final_prompt = prompt_wrapper.format(context=context_text, question=query)
            
            response = self.llm.invoke([HumanMessage(content=final_prompt)])
            return response.content

        except Exception as e:
            logger.error(f"Groq Generation Error: {str(e)}", exc_info=True)
            return "❌ AI Error: Groq quota or connection issue."

if __name__ == "__main__":
    engine = MedicalAIEngine()
    print("Groq Engine Test Complete.")