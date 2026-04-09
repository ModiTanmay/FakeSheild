import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_detection_to_reasons(detection_result: dict, original_profile: dict) -> list:
    """
    Convert ML detection scores to simple human-readable reasons
    """
    reasons = []
    scores = detection_result['scores']
    signals = detection_result['signals']
    
    # Bio similarity
    if scores.get('bio', 0) >= 0.70:
        reasons.append("Bio is copied from your profile")
    elif scores.get('bio', 0) >= 0.40:
        reasons.append("Bio is very similar to yours")
    
    # Username similarity
    if scores.get('username', 0) >= 0.80:
        reasons.append("Username is very similar to yours")
    
    # Name similarity
    if scores.get('name', 0) >= 0.95:
        reasons.append("Using your exact name")
    
    # Account age
    if signals.get('account_age'):
        reasons.append("Account created very recently")
    
    # Follower ratio
    if signals.get('follower_ratio'):
        reasons.append("Suspiciously low followers relative to following")
    
    return reasons


def classify_result(detection_result: dict) -> str:
    """
    Classify as Fake Account, Suspicious, or Legitimate
    """
    signals_count = detection_result['matching_signals_count']
    
    if signals_count >= 2:
        return "Fake Account"
    elif signals_count == 1:
        return "Suspicious"
    else:
        return "Legitimate"