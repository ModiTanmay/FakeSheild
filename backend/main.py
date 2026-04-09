

import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from routes import register_routes
from utils import log_error, error_response

app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def init_app():
    logger.info("Initializing FakeShield Backend...")
    register_routes(app)
    logger.info("Routes loaded successfully")
    register_error_handlers(app)
    logger.info("Error handlers loaded successfully")

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        log_error("404", str(error))
        return error_response("Endpoint not found", None, 404)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        log_error("405", str(error))
        return error_response("Method not allowed", None, 405)
    
    @app.errorhandler(500)
    def internal_error(error):
        log_error("500", str(error))
        return error_response("Internal server error", None, 500)
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        log_error("EXCEPTION", str(error))
        return error_response(f"Error: {str(error)}", None, 500)

@app.before_request
def log_request():
    from flask import request
    logger.info(f"REQUEST: {request.method} {request.path}")

@app.after_request
def log_response(response):
    from flask import request
    logger.info(f"RESPONSE: {response.status_code} {request.path}")
    return response

if __name__ == '__main__':
    init_app()
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("\nStarting FakeShield Backend")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"URL: http://localhost:{port}")
    print(f"Health Check: http://localhost:{port}/api/health\n")
    
    try:
        app.run(host=host, port=port, debug=debug, use_reloader=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        exit(1)
