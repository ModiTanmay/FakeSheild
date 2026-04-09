from fuzzywuzzy import fuzz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UsernameSimilarity:
    
    @staticmethod
    def calculate_similarity(username1: str, username2: str) -> float:
        """
        Calculate username similarity using FuzzyWuzzy
        
        Returns: float between 0 and 1 (1 = identical, 0 = completely different)
        """
        similarity_score = fuzz.ratio(username1.lower(), username2.lower())
        return similarity_score / 100.0
    
    @staticmethod
    def analyze(original_username: str, suspect_username: str) -> dict:
        """
        Analyze username similarity and return results
        """
        from config import Config
        
        score = UsernameSimilarity.calculate_similarity(original_username, suspect_username)
        
        return {
            'similarity_score': round(score, 2),
            'is_very_similar': score >= Config.USERNAME_SIMILARITY_THRESHOLD,
            'raw_score': score
        }