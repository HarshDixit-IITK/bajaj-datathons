"""Configuration management for the application."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # LLM Configuration - Choose provider
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # Options: openai, gemini
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Google Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # OCR Configuration
    OCR_ENGINE = os.getenv("OCR_ENGINE", "easyocr")
    
    # Azure Computer Vision (Optional)
    AZURE_CV_ENDPOINT = os.getenv("AZURE_CV_ENDPOINT", "")
    AZURE_CV_KEY = os.getenv("AZURE_CV_KEY", "")
    
    # Model Configuration
    GPT_MODEL = "gpt-4o"  # GPT-4 with vision support
    GPT_FALLBACK_MODEL = "gpt-4o-mini"  # Cheaper fallback
    MAX_TOKENS = 4096
    TEMPERATURE = 0.1  # Low temperature for more deterministic outputs
    USE_LLM = bool(OPENAI_API_KEY)  # Auto-disable LLM if no key


config = Config()

