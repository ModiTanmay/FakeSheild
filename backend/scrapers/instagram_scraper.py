import os
import time
import logging
import requests

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstagramScraper:
    """Scrape Instagram profiles via Apify actor runs."""

    BASE_URL = "https://api.apify.com/v2"
    ACTOR_ID = "shu8hvrXbJbY3Eb9W"
    REQUEST_TIMEOUT_SECONDS = 30
    POLLING_INTERVAL_SECONDS = 5
    MAX_WAIT_SECONDS = 300

    def __init__(self):
        self.apify_token = os.getenv("APIFY_TOKEN", "").strip()
        if not self.apify_token:
            raise RuntimeError("APIFY_TOKEN is not configured in environment variables")

    @staticmethod
    def normalize_username(value: str) -> str:
        """Normalize @username or URL into plain instagram username."""
        if not value:
            return ""

        cleaned = value.strip()
        if "instagram.com/" in cleaned:
            cleaned = cleaned.split("instagram.com/")[-1]
        cleaned = cleaned.strip("/")
        cleaned = cleaned.split("?")[0]
        cleaned = cleaned.split("#")[0]
        return cleaned.lstrip("@").lower()

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.apify_token}",
            "Content-Type": "application/json",
        }

    def _build_direct_urls(self, usernames: list[str]) -> list[str]:
        direct_urls = []
        for username in usernames:
            normalized = self.normalize_username(username)
            if normalized:
                direct_urls.append(f"https://www.instagram.com/{normalized}/")
        return direct_urls
    
    def scrape_profile(self, usernames: list[str], scan_id: str) -> list[dict]:
        """Run Apify actor and return raw profile objects from dataset items."""
        direct_urls = self._build_direct_urls(usernames)
        if not direct_urls:
            return []

        logger.info("Starting Apify run for %s usernames (scan_id=%s)", len(direct_urls), scan_id)

        run_response = requests.post(
            f"{self.BASE_URL}/acts/{self.ACTOR_ID}/runs",
            headers=self._headers(),
            json={
                "directUrls": direct_urls,
                "resultsType": "details",
                "resultsLimit": 1,
                "addParentData": False,
            },
            timeout=self.REQUEST_TIMEOUT_SECONDS,
        )
        run_response.raise_for_status()

        run_data = run_response.json().get("data", {})
        run_id = run_data.get("id")
        dataset_id = run_data.get("defaultDatasetId")

        if not run_id or not dataset_id:
            raise RuntimeError("Apify run started but missing run id or dataset id")

        deadline = time.time() + self.MAX_WAIT_SECONDS
        while time.time() < deadline:
            status_response = requests.get(
                f"{self.BASE_URL}/acts/{self.ACTOR_ID}/runs/{run_id}",
                headers=self._headers(),
                timeout=self.REQUEST_TIMEOUT_SECONDS,
            )
            status_response.raise_for_status()

            status = status_response.json().get("data", {}).get("status", "UNKNOWN")
            logger.debug("Apify polling (run_id=%s, status=%s)", run_id, status)

            if status == "SUCCEEDED":
                break
            if status in ("FAILED", "ABORTED", "TIMED-OUT"):
                raise RuntimeError(f"Apify run {run_id} ended with status: {status}")

            time.sleep(self.POLLING_INTERVAL_SECONDS)
        else:
            raise RuntimeError(f"Apify run {run_id} timed out after {self.MAX_WAIT_SECONDS} seconds")

        items_response = requests.get(
            f"{self.BASE_URL}/datasets/{dataset_id}/items",
            headers=self._headers(),
            params={"format": "json"},
            timeout=self.REQUEST_TIMEOUT_SECONDS,
        )
        items_response.raise_for_status()
        profiles = items_response.json()

        if not isinstance(profiles, list):
            return []
        return profiles
    
    def search_similar_usernames(self, original_username: str, limit: int = 10) -> list:
        """Generate common impersonation username variants."""
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