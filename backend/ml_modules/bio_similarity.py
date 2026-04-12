from sentence_transformers import SentenceTransformer, util
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BioSimilarity:
    def __init__(self):
        try:
            # Load pre-trained BERT model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("BERT model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading BERT model: {str(e)}")
            self.model = None
    
    def calculate_similarity(self, bio1: str, bio2: str) -> float:
        """
        Calculate bio similarity using BERT embeddings
        
        Returns: float between 0 and 1 (1 = identical, 0 = completely different)
        """
        if not bio1 or not bio2:
            return 0.0
        
        if self.model is None:
            return 0.0
        
        try:
            # Get embeddings
            embeddings1 = self.model.encode(bio1, convert_to_tensor=True)
            embeddings2 = self.model.encode(bio2, convert_to_tensor=True)
            
            # Calculate cosine similarity
            similarity = util.pytorch_cos_sim(embeddings1, embeddings2)
            
            return float(similarity[0][0])
        
        except Exception as e:
            logger.error(f"Error calculating bio similarity: {str(e)}")
            return 0.0
    
    def analyze(self, original_bio: str, suspect_bio: str) -> dict:
        """
        Analyze bio similarity and return results
        """
        from config import Config
        
        score = self.calculate_similarity(original_bio, suspect_bio)
        
        return {
            'similarity_score': round(score, 2),
            'is_high_similarity': score >= Config.BIO_SIMILARITY_THRESHOLD_HIGH,
            'is_medium_similarity': Config.BIO_SIMILARITY_THRESHOLD_MED <= score < Config.BIO_SIMILARITY_THRESHOLD_HIGH,
            'raw_score': score
        }