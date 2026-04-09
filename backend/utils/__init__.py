
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def success_response(message, data=None, status_code=200):
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    if data:
        response['data'] = data
    return response, status_code

def error_response(error, details=None, status_code=400):
    response = {
        'success': False,
        'error': error,
        'timestamp': datetime.now().isoformat()
    }
    if details:
        response['details'] = details
    return response, status_code

def validate_profile_url(url):
    if not url:
        return False, "URL is required"
    
    url = url.strip()
    
    if 'instagram.com' in url or '@' in url or url.isalnum():
        return True, None
    
    return False, "Invalid Instagram URL or username"

def extract_username(profile_url):
    if not profile_url:
        return None
    
    username = profile_url.replace('@', '')
    
    if 'instagram.com/' in username:
        username = username.split('instagram.com/')[-1]
    
    username = username.rstrip('/')
    
    return username.lower()

def validate_platforms(platforms):
    valid_platforms = ['instagram', 'twitter', 'linkedin', 'facebook', 'tiktok', 'reddit']
    
    if not platforms:
        return True, valid_platforms
    
    if not isinstance(platforms, list):
        return False, "Platforms must be a list"
    
    for platform in platforms:
        if platform not in valid_platforms:
            return False, f"Invalid platform: {platform}"
    
    return True, platforms

def calculate_username_similarity(username1, username2):
    if not username1 or not username2:
        return 0
    
    username1 = username1.lower()
    username2 = username2.lower()
    
    if username1 == username2:
        return 100
    
    if username1 in username2 or username2 in username1:
        return 75
    
    common = sum(1 for c in username1 if c in username2)
    similarity = (common / max(len(username1), len(username2))) * 100
    
    return int(similarity)

def calculate_risk_score(factors):
    score = 0
    
    if factors.get('uses_profile_photo'):
        score += 30
    if factors.get('uses_post_photos'):
        score += 25
    if factors.get('uses_captions'):
        score += 20
    if factors.get('similar_username'):
        score += 20
    if factors.get('very_new_account'):
        score += 15
    if factors.get('new_account'):
        score += 10
    if factors.get('bot_pattern'):
        score += 15
    if factors.get('suspicious_bio'):
        score += 10
    
    score = min(score, 100)
    
    return score

def get_risk_level(score):
    if score >= 80:
        return 'HIGH'
    elif score >= 50:
        return 'MEDIUM'
    else:
        return 'LOW'

def get_confidence(score):
    confidence = 50 + (score / 2)
    return int(min(confidence, 100))

def get_client_ip(request):
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    return request.remote_addr

def get_user_agent(request):
    return request.headers.get('User-Agent', 'Unknown')

def log_error(operation, error):
    logger.error(f"ERROR in {operation}: {str(error)}")

def log_scan_start(username, platforms):
    logger.info(f"SCAN START: username={username}, platforms={platforms}")

def log_scan_complete(username, total_found):
    logger.info(f"SCAN COMPLETE: username={username}, found={total_found}")
