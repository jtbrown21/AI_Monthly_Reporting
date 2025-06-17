"""
Main Flask application for SF Domain Reports.
"""
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify
from config.settings import config
from src.handlers.webhook import create_webhook_blueprint
from src.utils.logger import setup_logging
import logging

# Setup logging
logger = setup_logging(config.LOG_LEVEL)

def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Validate configuration
    config_errors = config.validate()
    if config_errors:
        logger.error(f"Configuration errors: {config_errors}")
        raise ValueError(f"Invalid configuration: {', '.join(config_errors)}")
    
    # Register blueprints
    app.register_blueprint(create_webhook_blueprint())
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            'status': 'healthy',
            'service': 'sf-domain-reports'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with basic info."""
        return jsonify({
            'service': 'SF Domain Reports Webhook Handler',
            'version': '1.0.0',
            'endpoints': {
                'webhook': '/webhook',
                'health': '/health'
            }
        }), 200
    
    logger.info("Application initialized successfully")
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0', 
        port=config.PORT,
        debug=config.DEBUG
    )

app = create_app()