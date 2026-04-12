from flask import request, jsonify
import logging
from datetime import datetime
from uuid import uuid4

from database import (
    create_scan_record,
    get_scan_history,
    get_scan_result,
    save_posts,
    save_profile,
    save_scan_result,
    update_scan_record,
)
from detection.detector import FakeAccountDetector
from detection.reason_converter import classify_result, convert_detection_to_reasons
from scrapers.instagram_scraper import InstagramScraper

logger = logging.getLogger(__name__)


def _extract_username(profile_url: str) -> str:
    if not profile_url:
        return ""

    cleaned = profile_url.strip()
    if "instagram.com/" in cleaned:
        cleaned = cleaned.split("instagram.com/")[-1]
    cleaned = cleaned.strip("/")
    cleaned = cleaned.split("?")[0]
    cleaned = cleaned.split("#")[0]
    return cleaned.lstrip("@").lower()


def _to_detector_profile(profile: dict) -> dict:
    about = profile.get("about") or {}
    joined_ts = about.get("date_joined_as_timestamp")
    account_created = None
    if isinstance(joined_ts, (int, float)):
        account_created = datetime.utcfromtimestamp(joined_ts)

    return {
        "username": (profile.get("username") or "").lower(),
        "name": profile.get("fullName", "") or "",
        "bio": profile.get("biography", "") or "",
        "followers": profile.get("followersCount", 0) or 0,
        "following": profile.get("followsCount", 0) or 0,
        "account_created": account_created,
    }


def _risk_level(classification: str) -> str:
    if classification == "Fake Account":
        return "HIGH"
    if classification == "Suspicious":
        return "MEDIUM"
    return "LOW"

def register_routes(app):
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'FakeShield backend is running',
            'timestamp': datetime.now().isoformat()
        }), 200
    
    @app.route('/api/detect-impersonation', methods=['POST'])
    def detect_impersonation():
        scan_id = None
        try:
            logger.info("Scan request received")

            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400

            profile_url = data.get('profile_url')
            platforms = data.get('platforms', ['instagram'])

            if not profile_url:
                return jsonify({
                    'success': False,
                    'error': 'profile_url is required'
                }), 400

            username = _extract_username(profile_url)
            if not username:
                return jsonify({
                    'success': False,
                    'error': 'Could not parse Instagram username from profile_url'
                }), 400

            scan_id = str(uuid4())
            create_scan_record(scan_id, profile_url, 'instagram')

            logger.info(f"Scanning: {profile_url} on {platforms}")
            scraper = InstagramScraper()
            detector = FakeAccountDetector()

            candidates = [username] + scraper.search_similar_usernames(username, limit=10)
            deduped_candidates = list(dict.fromkeys(candidates))

            scraped_profiles = scraper.scrape_profile(deduped_candidates, scan_id)
            if not scraped_profiles:
                update_scan_record(scan_id, 'completed', 0, 0)
                empty_results = {'instagram': {'found': 0, 'fake_accounts': []}}
                for platform in platforms:
                    if platform != 'instagram':
                        empty_results[platform] = {'found': 0, 'fake_accounts': []}

                response_payload = {
                    'success': True,
                    'message': 'Scan complete. Found 0 suspicious accounts',
                    'scan_id': scan_id,
                    'timestamp': datetime.now().isoformat(),
                    'results': empty_results,
                    'summary': {
                        'total_accounts_found': 0,
                        'high_risk': 0,
                        'medium_risk': 0,
                        'platforms_scanned': len(platforms)
                    }
                }
                save_scan_result(scan_id, response_payload)
                return jsonify(response_payload), 200

            total_posts = 0
            for profile in scraped_profiles:
                save_profile(profile, scan_id)
                total_posts += save_posts(profile, scan_id)

            original_profile = None
            for profile in scraped_profiles:
                scraped_username = (profile.get('username') or '').lower()
                if scraped_username == username:
                    original_profile = profile
                    break

            if original_profile is None:
                original_profile = scraped_profiles[0]

            original_detector_profile = _to_detector_profile(original_profile)
            fake_accounts = []

            for profile in scraped_profiles:
                suspect_username = (profile.get('username') or '').lower()
                if suspect_username == original_detector_profile.get('username'):
                    continue

                suspect_detector_profile = _to_detector_profile(profile)
                detection = detector.detect(original_detector_profile, suspect_detector_profile)
                classification = classify_result(detection)
                if classification == 'Legitimate':
                    continue

                reasons = convert_detection_to_reasons(detection, original_detector_profile)
                fake_accounts.append({
                    'username': profile.get('username'),
                    'url': profile.get('url') or f"https://instagram.com/{suspect_username}",
                    'followers': profile.get('followersCount', 0),
                    'risk_level': _risk_level(classification),
                    'confidence': int((detection.get('confidence', 0) or 0) * 100),
                    'reasons': reasons,
                })

            update_scan_record(
                scan_id,
                'completed',
                len(scraped_profiles),
                total_posts,
            )

            results = {
                'instagram': {
                    'found': len(fake_accounts),
                    'fake_accounts': fake_accounts,
                }
            }

            for platform in platforms:
                if platform != 'instagram':
                    results[platform] = {'found': 0, 'fake_accounts': []}

            total_found = sum(r['found'] for r in results.values())
            high_risk = sum(1 for account in fake_accounts if account['risk_level'] == 'HIGH')
            medium_risk = sum(1 for account in fake_accounts if account['risk_level'] == 'MEDIUM')

            response_payload = {
                'success': True,
                'message': f'Scan complete. Found {total_found} suspicious accounts',
                'scan_id': scan_id,
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'summary': {
                    'total_accounts_found': total_found,
                    'high_risk': high_risk,
                    'medium_risk': medium_risk,
                    'platforms_scanned': len(platforms)
                }
            }

            save_scan_result(scan_id, response_payload)
            return jsonify(response_payload), 200

        except Exception as e:
            logger.error(f"Error in detect_impersonation: {str(e)}")
            if scan_id:
                try:
                    update_scan_record(scan_id, 'failed', 0, 0)
                except Exception:
                    logger.exception('Failed to update scan record status to failed')
            return jsonify({
                'success': False,
                'error': f'Scan failed: {str(e)}'
            }), 500
    
    @app.route('/api/results/<scan_id>', methods=['GET'])
    def get_results(scan_id):
        try:
            logger.info(f"Fetching results for scan: {scan_id}")
            results = get_scan_result(scan_id)
            if not results:
                return jsonify({
                    'success': False,
                    'error': 'Scan result not found'
                }), 404

            return jsonify({
                'success': True,
                'data': results
            }), 200
        
        except Exception as e:
            logger.error(f"Error in get_results: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/history', methods=['GET'])
    def get_history():
        try:
            logger.info("Fetching scan history")
            history = get_scan_history(limit=100)
            
            return jsonify({
                'success': True,
                'data': history,
                'count': len(history)
            }), 200
        
        except Exception as e:
            logger.error(f"Error in get_history: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/report', methods=['POST'])
    def report_account():
        try:
            logger.info("Received report request")
            
            data = request.get_json()
            username = data.get('username')
            platform = data.get('platform')
            reason = data.get('reason')
            
            if not username or not platform:
                return jsonify({
                    'success': False,
                    'error': 'username and platform are required'
                }), 400
            
            logger.info(f"Reporting {username} on {platform}")
            
            return jsonify({
                'success': True,
                'message': f'Report submitted for {username}',
                'report_id': f'report_{datetime.now().timestamp()}',
                'status': 'pending_review'
            }), 200
        
        except Exception as e:
            logger.error(f"Error in report_account: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
