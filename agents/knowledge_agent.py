"""Knowledge Agent - handles RAG-based queries using Infinitepay documentation."""
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from models import AgentType, KnowledgeResponse, ChatMessage
from utils.logger import StructuredLogger
from utils.security import SecurityValidator
from config import Config

class KnowledgeAgent:
    """Knowledge agent that uses RAG to answer questions about Infinitepay."""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.logger = StructuredLogger("KnowledgeAgent")
        self.security_validator = SecurityValidator()
        self.vectorstore = None
        self.qa_chain = None
        self._initialize_rag_system()
    
    def _scrape_infinitepay_docs(self) -> List[Dict[str, str]]:
        """Scrape Infinitepay documentation and return structured content."""
        try:
            self.logger.log_info("Starting documentation scraping...")
            
            # Main documentation page
            response = requests.get(Config.KNOWLEDGE_BASE_URL, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content from the page
            content = []
            
            # Get main content areas
            main_content = soup.find('main') or soup.find('div', class_='content') or soup.find('body')
            
            if main_content:
                # Extract headings and their content
                for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div']):
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:  # Filter out very short text
                        content.append({
                            'text': text,
                            'tag': element.name,
                            'source': Config.KNOWLEDGE_BASE_URL
                        })
            
            # Also try to find navigation links to other documentation pages
            nav_links = soup.find_all('a', href=True)
            additional_pages = []
            
            for link in nav_links[:10]:  # Limit to first 10 links to avoid too many requests
                href = link.get('href')
                if href and not href.startswith('http'):
                    href = Config.KNOWLEDGE_BASE_URL.rstrip('/') + '/' + href.lstrip('/')
                
                if href and 'infinitepay.io' in href:
                    try:
                        page_response = requests.get(href, timeout=10)
                        if page_response.status_code == 200:
                            page_soup = BeautifulSoup(page_response.content, 'html.parser')
                            page_content = page_soup.get_text(strip=True)
                            if page_content and len(page_content) > 100:
                                content.append({
                                    'text': page_content[:2000],  # Limit content length
                                    'tag': 'page',
                                    'source': href
                                })
                    except:
                        continue  # Skip pages that fail to load
            
            # If no content was scraped, add comprehensive fallback content
            if not content:
                content = self._get_fallback_content()
            
            self.logger.log_info(f"Scraped {len(content)} content pieces from documentation")
            return content
            
        except Exception as e:
            self.logger.log_error(AgentType.KNOWLEDGE, f"Documentation scraping failed: {str(e)}")
            # Return comprehensive fallback content
            return self._get_fallback_content()
    
    def _get_fallback_content(self) -> List[Dict[str, str]]:
        """Get comprehensive fallback content about Infinitepay."""
        return [
            {
                'text': 'Infinitepay é uma plataforma de pagamentos brasileira que oferece soluções completas para e-commerce e varejo. A plataforma permite processar pagamentos online de forma segura e eficiente.',
                'tag': 'fallback',
                'source': Config.KNOWLEDGE_BASE_URL
            },
            {
                'text': 'A API do Infinitepay permite integração com sistemas de e-commerce, oferecendo endpoints para processamento de pagamentos, consulta de transações e gestão de webhooks.',
                'tag': 'fallback',
                'source': Config.KNOWLEDGE_BASE_URL
            },
            {
                'text': 'Para integrar com a API do Infinitepay, você precisa de credenciais de API (API Key e API Secret), que podem ser obtidas no painel administrativo da plataforma.',
                'tag': 'fallback',
                'source': Config.KNOWLEDGE_BASE_URL
            },
            {
                'text': 'O Infinitepay suporta diversos métodos de pagamento incluindo cartões de crédito, PIX, boleto bancário e débito online, oferecendo flexibilidade para os clientes.',
                'tag': 'fallback',
                'source': Config.KNOWLEDGE_BASE_URL
            },
            {
                'text': 'Webhooks são notificações automáticas enviadas pelo Infinitepay para informar sobre mudanças no status de transações, permitindo atualizações em tempo real no seu sistema.',
                'tag': 'fallback',
                'source': Config.KNOWLEDGE_BASE_URL
            },
            {
                'text': 'A documentação completa da API do Infinitepay está disponível em https://ajuda.infinitepay.io/pt-BR/ com exemplos de código e guias de integração.',
                'tag': 'fallback',
                'source': Config.KNOWLEDGE_BASE_URL
            }
        ]
    
    def _create_vectorstore(self, documents: List[Dict[str, str]]) -> FAISS:
        """Create FAISS vector store from documents."""
        try:
            # Extract text content
            texts = [doc['text'] for doc in documents]
            sources = [doc['source'] for doc in documents]
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            chunks = text_splitter.create_documents(texts, metadatas=[{'source': source} for source in sources])
            
            # Create embeddings
            embeddings = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY)
            
            # Create vector store
            vectorstore = FAISS.from_documents(chunks, embeddings)
            
            self.logger.log_info(f"Created vector store with {len(chunks)} chunks")
            return vectorstore
            
        except Exception as e:
            self.logger.log_error(AgentType.KNOWLEDGE, f"Vector store creation failed: {str(e)}")
            raise
    
    def _initialize_rag_system(self):
        """Initialize the RAG system with documentation."""
        try:
            self.logger.log_info("Initializing RAG system...")
            
            # Check if OpenAI API key is available
            if not Config.OPENAI_API_KEY:
                self.logger.log_error(AgentType.KNOWLEDGE, "OpenAI API key not configured")
                self.vectorstore = None
                self.qa_chain = None
                return
            
            # Scrape documentation
            self.logger.log_info("Scraping Infinitepay documentation...")
            documents = self._scrape_infinitepay_docs()
            
            if not documents:
                self.logger.log_error(AgentType.KNOWLEDGE, "No documents scraped from Infinitepay")
                self.vectorstore = None
                self.qa_chain = None
                return
            
            # Create vector store
            self.logger.log_info("Creating vector store...")
            self.vectorstore = self._create_vectorstore(documents)
            
            # Create QA chain
            self.logger.log_info("Creating QA chain...")
            llm = ChatOpenAI(
                api_key=Config.OPENAI_API_KEY,
                model_name=Config.KNOWLEDGE_MODEL,
                temperature=0.1
            )
            
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
            
            self.logger.log_info("RAG system initialized successfully")
            
        except Exception as e:
            self.logger.log_error(AgentType.KNOWLEDGE, f"RAG system initialization failed: {str(e)}")
            import traceback
            self.logger.log_error(AgentType.KNOWLEDGE, f"Traceback: {traceback.format_exc()}")
            # Initialize with empty vector store as fallback
            self.vectorstore = None
            self.qa_chain = None
    
    def _extract_sources(self, source_documents) -> List[str]:
        """Extract unique sources from retrieved documents."""
        sources = set()
        for doc in source_documents:
            if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                sources.add(doc.metadata['source'])
        return list(sources)
    
    def answer_question(self, chat_message: ChatMessage) -> KnowledgeResponse:
        """Answer user question using RAG system."""
        start_time = time.time()
        
        try:
            # Sanitize input message
            sanitized_message = self.security_validator.sanitize_input(chat_message.message)
            
            # Check for prompt injection
            injection_check = self.security_validator.detect_prompt_injection(sanitized_message)
            if injection_check["is_suspicious"]:
                self.logger.log_info(
                    "Prompt injection detected in knowledge query",
                    metadata={
                        "confidence": injection_check["confidence"],
                        "patterns": injection_check["patterns_found"]
                    }
                )
                
                return KnowledgeResponse(
                    answer="Desculpe, mas sua pergunta contém instruções não permitidas. Por favor, faça uma pergunta sobre Infinitepay ou matemática.",
                    sources=[Config.KNOWLEDGE_BASE_URL],
                    execution_time=time.time() - start_time,
                    timestamp=chat_message.timestamp,
                    user_message=chat_message.message
                )
            
            if not self.qa_chain:
                # Fallback response if RAG system is not available
                return KnowledgeResponse(
                    answer="Desculpe, mas a base de conhecimento está temporariamente indisponível. Tente novamente mais tarde ou visite a documentação do Infinitepay diretamente.",
                    sources=[Config.KNOWLEDGE_BASE_URL],
                    execution_time=time.time() - start_time,
                    timestamp=chat_message.timestamp,
                    user_message=chat_message.message
                )
            
            # Query the RAG system with sanitized message
            result = self.qa_chain({"query": sanitized_message})
            
            # Extract answer and sources
            answer = result["result"]
            sources = self._extract_sources(result.get("source_documents", []))
            
            # If no sources found, add the main documentation URL
            if not sources:
                sources = [Config.KNOWLEDGE_BASE_URL]
            
            execution_time = time.time() - start_time
            
            # Log execution with full observability
            self.logger.log_agent_execution(
                agent_type=AgentType.KNOWLEDGE,
                message=chat_message.message,
                execution_time=execution_time,
                conversation_id=chat_message.conversation_id,
                user_id=chat_message.user_id,
                processed_content=answer[:200] + "..." if len(answer) > 200 else answer,
                metadata={
                    "sources_count": len(sources),
                    "sources": sources,
                    "rag_system_available": True
                }
            )
            
            return KnowledgeResponse(
                answer=answer,
                sources=sources,
                execution_time=execution_time,
                timestamp=chat_message.timestamp,
                user_message=chat_message.message
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.log_error(
                AgentType.KNOWLEDGE, 
                f"Knowledge query failed: {str(e)}",
                conversation_id=chat_message.conversation_id,
                user_id=chat_message.user_id,
                execution_time=execution_time,
                metadata={"error_type": "knowledge_query_failure"}
            )
            
            return KnowledgeResponse(
                answer="Desculpe, ocorreu um erro ao processar sua pergunta. Tente reformular sua pergunta ou visite a documentação do Infinitepay para mais informações.",
                sources=[Config.KNOWLEDGE_BASE_URL],
                execution_time=execution_time,
                timestamp=chat_message.timestamp,
                user_message=chat_message.message
            )