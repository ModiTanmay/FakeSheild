from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BehavioralAnalysis:
    
    @staticmethod
    def calculate_follower_ratio(followers: int, following: int) -> float:
        """
        Calculate follower/following ratio
        Fake accounts often have very low follower ratio
        """
        if following == 0:
            return 0.0
        
        return followers / following
    
    @staticmethod
    def analyze_account_age(account_created) -> dict:
        """
        Analyze account creation date
        """
        from config import Config
        
        if not account_created:
            return {
                'account_age_days': None,
                'is_very_new': False,
                'is_new': False
            }
        
        try:
            days_old = (datetime.now() - account_created).days
            
            return {
                'account_age_days': days_old,
                'is_very_new': days_old <= Config.ACCOUNT_AGE_VERY_NEW,
                'is_new': days_old <= Config.ACCOUNT_AGE_NEW,
                'raw_days': days_old
            }
        except Exception as e:
            logger.error(f"Error analyzing account age: {str(e)}")
            return {
                'account_age_days': None,
                'is_very_new': False,
                'is_new': False
            }
    
    @staticmethod
    def analyze(profile_data: dict) -> dict:
        """
        Behavioral analysis of profile
        """
        from config import Config
        
        follower_ratio = BehavioralAnalysis.calculate_follower_ratio(
            profile_data.get('followers', 0),
            profile_data.get('following', 1)
        )
        
        account_age_analysis = BehavioralAnalysis.analyze_account_age(
            profile_data.get('account_created')
        )
        
        return {
            'follower_ratio': round(follower_ratio, 2),
            'is_suspicious_ratio': follower_ratio <= Config.FOLLOWER_RATIO_SUSPICIOUS,
            'account_age': account_age_analysis,
            'raw_ratio': follower_ratio
        }