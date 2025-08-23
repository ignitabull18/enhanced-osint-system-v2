#!/usr/bin/env python3
"""
Enhanced OSINT System v2.0 - Coolify Deployment
Simplified Flask web service for testing
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Root endpoint providing system information."""
    return jsonify({
        "system": "Enhanced OSINT System v2.0",
        "status": "Operational",
        "message": "Welcome to the Enhanced OSINT System API!",
        "version": "2.0",
        "timestamp": datetime.now().isoformat(),
        "api_endpoints": {
            "/health": "Health check endpoint",
            "/status": "Current system status"
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint for Coolify."""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "2.0"
    }), 200

@app.route('/status')
def get_status():
    """Returns the current system status."""
    return jsonify({
        "status": "idle",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0"
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8002))
    logger.info(f"Starting Enhanced OSINT System on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)