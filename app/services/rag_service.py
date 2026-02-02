import os
from typing import List, Tuple
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document



from app.config import settings

class RAGService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL
        )
        self.vector_store = None
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS_PER_RESPONSE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize or load the vector store."""
        persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        try:
            # Try to load existing vector store
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
            print("✅ Loaded existing vector store")
        except Exception as e:
            print(f"⚠️ No existing vector store found. Creating new one...")
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
            # Add sample data
            self._add_sample_data()
    
    def _add_sample_data(self):
        """Add sample WorknAI content to vector store."""
        sample_docs = [
            Document(
                page_content="""WorknAI offers comprehensive AI and Machine Learning courses designed for beginners and professionals. 
                Our flagship programs include:
                - AI/ML Foundation Course (3 months)
                - Python for Data Science Bootcamp (2 months)
                - Advanced Deep Learning Specialization (4 months)
                - Career Mentorship Program (ongoing support)
                
                All courses include hands-on projects, industry-relevant case studies, and placement assistance.""",
                metadata={"source": "courses_overview", "type": "website"}
            ),
            Document(
                page_content="""To get started with AI/ML at WorknAI:
                1. Assess your current skill level (beginner, intermediate, advanced)
                2. Choose the right course based on your goals
                3. Complete the enrollment process
                4. Access our learning platform and resources
                5. Join our community of learners
                
                Prerequisites: Basic programming knowledge is helpful but not mandatory for beginner courses.""",
                metadata={"source": "getting_started", "type": "website"}
            ),
            Document(
                page_content="""WorknAI Career Mentorship includes:
                - One-on-one sessions with industry experts
                - Resume and portfolio review
                - Interview preparation and mock interviews
                - Job search strategies and networking tips
                - Salary negotiation guidance
                - Continuous support even after placement
                
                Our mentors have experience at top companies like Google, Microsoft, Amazon, and Indian startups.""",
                metadata={"source": "mentorship", "type": "website"}
            ),
            Document(
                page_content="""Python is essential for AI/ML because:
                - Rich ecosystem of libraries (NumPy, Pandas, Scikit-learn, TensorFlow, PyTorch)
                - Easy to learn and read
                - Strong community support
                - Industry standard for data science and machine learning
                
                WorknAI's Python courses cover: basics, data structures, NumPy, Pandas, visualization, and ML libraries.""",
                metadata={"source": "python_importance", "type": "website"}
            ),
            Document(
                page_content="""AI/ML Career Paths at WorknAI:
                1. Machine Learning Engineer - Build and deploy ML models
                2. Data Scientist - Analyze data and create insights
                3. AI Research Scientist - Develop new AI algorithms
                4. MLOps Engineer - Manage ML infrastructure
                5. NLP Engineer - Work with language models
                
                Average salaries in India: 8-25 LPA for freshers, 25-50 LPA for experienced professionals.""",
                metadata={"source": "career_paths", "type": "website"}
            ),
        ]
        
        self.vector_store.add_documents(sample_docs)
        print("✅ Added sample data to vector store")
    
    def add_documents(self, texts: List[str], metadatas: List[dict] = None):
        """Add new documents to the vector store."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        docs = []
        for i, text in enumerate(texts):
            chunks = text_splitter.split_text(text)
            for chunk in chunks:
                metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
                docs.append(Document(page_content=chunk, metadata=metadata))
        
        self.vector_store.add_documents(docs)
        print(f"✅ Added {len(docs)} document chunks to vector store")
    
    def retrieve_context(self, query: str, k: int = 3) -> Tuple[str, List[str]]:
        """Retrieve relevant context from vector store."""
        try:
            results = self.vector_store.similarity_search(query, k=k)
            
            context = "\n\n".join([doc.page_content for doc in results])
            sources = [doc.metadata.get("source", "unknown") for doc in results]
            
            return context, sources
        except Exception as e:
            print(f"⚠️ Error retrieving context: {e}")
            return "No relevant context found.", []
    
    def generate_response(self, prompt: str) -> str:
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now."

# Global instance
rag_service = None

def get_rag_service():
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service
