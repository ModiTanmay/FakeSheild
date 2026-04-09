import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "fakeshield")
    
    # API Keys
    APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")
    
    # Detection thresholds
    BIO_SIMILARITY_THRESHOLD_HIGH = 0.70
    BIO_SIMILARITY_THRESHOLD_MED = 0.40
    USERNAME_SIMILARITY_THRESHOLD = 0.80
    PHOTO_SIMILARITY_THRESHOLD = 0.75
    
    # Account age thresholds (in days)
    ACCOUNT_AGE_VERY_NEW = 30
    ACCOUNT_AGE_NEW = 90
    
    # Follower ratio threshold
    FOLLOWER_RATIO_SUSPICIOUS = 0.1