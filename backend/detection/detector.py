from ml_modules.bio_similarity import BioSimilarity
from ml_modules.username_similarity import UsernameSimilarity
from ml_modules.behavioral import BehavioralAnalysis
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FakeAccountDetector:
    def __init__(self):
        self.bio_analyzer = BioSimilarity()
    
    def detect(self, original_profile: dict, suspect_profile: dict) -> dict:
        """
        Run complete ML detection pipeline
        
        Returns:
        {
            'is_fake': bool,
            'confidence': float,
            'signals': {
                'bio_match': bool,
                'username_match': bool,
                'name_match': bool,
                'follower_ratio': bool,
                'account_age': bool
            },
            'scores': {
                'bio_score': float,
                'username_score': float,
                'name_score': float,
                ...
            },
            'matching_signals_count': int
        }
        """
        
        signals = {}
        scores = {}
        
        # 1. Bio Similarity Analysis
        bio_analysis = self.bio_analyzer.analyze(
            original_profile.get('bio', ''),
            suspect_profile.get('bio', '')
        )
        scores['bio'] = bio_analysis['similarity_score']
        signals['bio_match'] = bio_analysis['is_high_similarity']
        
        # 2. Username Similarity
        username_analysis = UsernameSimilarity.analyze(
            original_profile.get('username', ''),
            suspect_profile.get('username', '')
        )
        scores['username'] = username_analysis['similarity_score']
        signals['username_match'] = username_analysis['is_very_similar']
        
        # 3. Name Similarity
        name_similarity = UsernameSimilarity.calculate_similarity(
            original_profile.get('name', ''),
            suspect_profile.get('name', '')
        )
        scores['name'] = round(name_similarity, 2)
        signals['name_match'] = name_similarity >= 0.9
        
        # 4. Behavioral Analysis
        behavioral_analysis = BehavioralAnalysis.analyze(suspect_profile)
        scores['follower_ratio'] = behavioral_analysis['follower_ratio']
        signals['follower_ratio'] = behavioral_analysis['is_suspicious_ratio']
        
        account_age = behavioral_analysis['account_age']
        signals['account_age'] = account_age.get('is_very_new', False)
        
        # Count matching signals
        matching_signals = sum(1 for v in signals.values() if v)
        
        # Determine if fake (2 or more signals match)
        is_fake = matching_signals >= 2
        
        # Calculate confidence
        confidence = min(matching_signals / 5, 1.0)  # Normalized to 0-1
        
        return {
            'is_fake': is_fake,
            'confidence': round(confidence, 2),
            'signals': signals,
            'scores': scores,
            'matching_signals_count': matching_signals
        }