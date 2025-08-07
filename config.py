"""
Configuration file for Event Situational Awareness System
"""
import os
from typing import List
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
    
    # Zone Configuration - Dynamic based on available videos
    @classmethod
    def get_zones_for_videos(cls, video_count: int) -> List[str]:
        """Generate zone names based on number of videos available"""
        zone_names = ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E", "Zone F"]
        return zone_names[:max(1, video_count)]  # At least one zone
    
    # Default zones (fallback)
    ZONES = ["Zone A", "Zone B"]  # Default to 2 zones to match current videos
    
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