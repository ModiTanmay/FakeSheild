

from flask import request, jsonify
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

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
            
            logger.info(f"Scanning: {profile_url} on {platforms}")
            
            results = {
                'instagram': {
                    'found': 2,
                    'fake_accounts': [
                        {
                            'username': 'john_doe_official',
                            'url': 'https://instagram.com/john_doe_official',
                            'followers': 150,
                            'risk_level': 'HIGH',
                            'confidence': 98,
                            'reasons': [
                                'Using your profile photo',
                                'Similar username pattern',
                                'Account created 15 days ago',
                                'Suspicious follower pattern'
                            ]
                        },
                        {
                            'username': 'john_doe.real',
                            'url': 'https://instagram.com/john_doe.real',
                            'followers': 100,
                            'risk_level': 'MEDIUM',
                            'confidence': 85,
                            'reasons': [
                                'Reposting your content',
                                'Similar bio text'
                            ]
                        }
                    ]
                },
                'twitter': {
                    'found': 1,
                    'fake_accounts': [
                        {
                            'username': 'john_doe_twitter',
                            'url': 'https://twitter.com/john_doe_twitter',
                            'followers': 50,
                            'risk_level': 'HIGH',
                            'confidence': 92,
                            'reasons': [
                                'Similar username',
                                'Same bio as Instagram'
                            ]
                        }
                    ]
                },
                'linkedin': {
                    'found': 0,
                    'fake_accounts': []
                }
            }
            
            total_found = sum(r['found'] for r in results.values())
            
            return jsonify({
                'success': True,
                'message': f'Scan complete. Found {total_found} suspicious accounts',
                'scan_id': f'scan_{datetime.now().timestamp()}',
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'summary': {
                    'total_accounts_found': total_found,
                    'high_risk': 2,
                    'medium_risk': 1,
                    'platforms_scanned': len(platforms)
                }
            }), 200
        
        except Exception as e:
            logger.error(f"Error in detect_impersonation: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Scan failed: {str(e)}'
            }), 500
    
    @app.route('/api/results/<scan_id>', methods=['GET'])
    def get_results(scan_id):
        try:
            logger.info(f"Fetching results for scan: {scan_id}")
            
            results = {
                'scan_id': scan_id,
                'timestamp': datetime.now().isoformat(),
                'results': {
                    'instagram': {
                        'found': 2,
                        'fake_accounts': [
                            {
                                'username': 'john_doe_official',
                                'followers': 150,
                                'risk_level': 'HIGH',
                                'confidence': 98
                            }
                        ]
                    }
                }
            }
            
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
            
            history = [
                {
                    'scan_id': 'scan_1',
                    'profile_url': '@john_doe',
                    'timestamp': '2024-04-08T10:30:00',
                    'total_found': 3,
                    'platforms': ['instagram', 'twitter']
                },
                {
                    'scan_id': 'scan_2',
                    'profile_url': '@jane_smith',
                    'timestamp': '2024-04-07T15:45:00',
                    'total_found': 1,
                    'platforms': ['instagram']
                }
            ]
            
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
