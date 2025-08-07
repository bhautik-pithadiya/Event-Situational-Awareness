"""
Configuration file for Event Situational Awareness System
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the application"""
    
    # Google Gemini API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # Video Processing Configuration
    VIDEO_FRAME_SKIP_THRESHOLD = 0.3  # Motion detection threshold
    MAX_FRAMES_PER_VIDEO = 10  # Maximum frames to extract per video
    FRAME_EXTRACTION_INTERVAL = 30  # Extract frame every N frames
    
    # Agent Configuration
    VISION_MODEL = "gemini-1.5-pro"
    TEXT_MODEL = "gemini-1.5-pro"
    
    # File Paths
    DATA_DIR = "data"
    VIDEOS_DIR = "videos"
    FIELD_REPORTS_FILE = "data/field_reports.txt"
    
    # Zone Configuration
    ZONES = ["Zone A", "Zone B", "Zone C", "Zone D"]
    
    # Streamlit Configuration
    PAGE_TITLE = "Event Situational Awareness Dashboard"
    PAGE_ICON = "🚨"
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your .env file.")
        
        return True

# Initialize configuration
config = Config()