import instaloader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        self.loader = instaloader.Instaloader(
            quiet=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    
    def extract_username_from_url(self, url: str) -> str:
        """
        Extract Instagram username from URL
        Example: https://instagram.com/john_doe -> john_doe
        """
        url = url.rstrip('/').strip()
        return url.split('/')[-1]
    
    def scrape_profile(self, username: str):
        """
        Scrape Instagram profile data
        
        Returns:
        {
            'username': str,
            'name': str,
            'bio': str,
            'followers': int,
            'following': int,
            'post_count': int,
            'profile_pic_url': str,
            'platform': 'instagram'
        }
        """
        try:
            profile = self.loader.context.username_to_profile(username)
            
            return {
                'username': profile.username,
                'name': profile.full_name,
                'bio': profile.biography,
                'followers': profile.follower_count,
                'following': profile.following_count,
                'post_count': profile.mediacount,
                'profile_pic_url': profile.profile_pic_url,
                'platform': 'instagram'
            }
        
        except instaloader.exceptions.ProfileNotExistsException:
            logger.error(f"Profile {username} does not exist")
            return None
        except Exception as e:
            logger.error(f"Error scraping {username}: {str(e)}")
            return None
    
    def search_similar_usernames(self, original_username: str, limit: int = 10) -> list:
        """
        Generate similar usernames (common impersonation patterns)
        """
        variations = [
            f"{original_username}official",
            f"{original_username}_official",
            f"official_{original_username}",
            f"{original_username}real",
            f"the{original_username}",
            f"{original_username}2",
            f"{original_username}1",
            f"{original_username}_",
            f"_{original_username}",
            f"{original_username}__",
        ]
        
        return variations[:limit]