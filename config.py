"""Configuration settings for the modular chatbot."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # OpenAI API configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Knowledge base configuration
    KNOWLEDGE_BASE_URL = "https://ajuda.infinitepay.io/pt-BR/"
    
    # Redis configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    
    # Agent configuration
    ROUTER_MODEL = "gpt-3.5-turbo"
    KNOWLEDGE_MODEL = "gpt-3.5-turbo"
    MATH_MODEL = "gpt-3.5-turbo"
    
    # API configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_DEBUG = os.getenv("API_DEBUG", "false").lower() == "true"
