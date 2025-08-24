#!/usr/bin/env python3
"""
Enhanced OSINT System v2.0 - Coolify Deployment
Full Flask web service with PocketBase integration
"""

import os
import sys
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request, jsonify
from config.settings import get_config, Config
from core.enrichment import process_real_leads_production_parallel
from core.pocketbase_client import PocketBaseClient

# Initialize Flask app
app = Flask(__name__)

# Global processing status
processing_status = {
    'current_job': None,
    'status': 'idle',
    'start_time': None,
    'end_time': None,
    'total_leads': 0,
    'processed_leads': 0,
    'successful_leads': 0,
    'failed_leads': 0,
    'progress_percentage': 0.0,
    'last_update': None,
    'error_message': None
}

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper(),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize PocketBase client globally (keep client even if auth fails)
pb_client: Optional[PocketBaseClient] = None
try:
    pb_client = PocketBaseClient()
    pb_client.authenticate()  # Best effort; keep client regardless
except Exception as e:
    logger.error(f"Error initializing PocketBase client: {e}")
    pb_client = PocketBaseClient()  # keep a bare client for health and open rules

def run_osint_processing(job_id: str, config: Config, leads_to_process: int):
    """Wrapper function to run OSINT processing in a separate thread."""
    global processing_status
    logger.info(f"Starting OSINT processing job: {job_id}")

    processing_status['current_job'] = job_id
    processing_status['status'] = 'running'
    processing_status['start_time'] = datetime.now().isoformat()
    processing_status['total_leads'] = leads_to_process
    processing_status['processed_leads'] = 0
    processing_status['successful_leads'] = 0
    processing_status['failed_leads'] = 0
    processing_status['progress_percentage'] = 0.0
    processing_status['last_update'] = datetime.now().isoformat()
    processing_status['error_message'] = None

    try:
        # Call the main OSINT processing function
        process_real_leads_production_parallel(
            num_leads=leads_to_process,
            max_workers=config.processing.max_workers,
            batch_size=config.processing.batch_size,
            pb_client=pb_client,
            processing_status_ref=processing_status
        )
        processing_status['status'] = 'completed'
        logger.info(f"OSINT processing job {job_id} completed successfully.")
    except Exception as e:
        processing_status['status'] = 'failed'
        processing_status['error_message'] = str(e)
        logger.error(f"OSINT processing job {job_id} failed: {e}", exc_info=True)
    finally:
        processing_status['end_time'] = datetime.now().isoformat()
        processing_status['last_update'] = datetime.now().isoformat()
        if processing_status['status'] == 'running':
            processing_status['status'] = 'interrupted'
        logger.info(f"OSINT processing job {job_id} finished with status: {processing_status['status']}")

@app.route('/')
def index():
    """Root endpoint providing system information."""
    config = get_config()
    return jsonify({
        "system": "Enhanced OSINT System v2.0",
        "status": "Operational",
        "message": "Welcome to the Enhanced OSINT System API!",
        "version": "2.0",
        "environment": config.environment,
        "database_configured": "PocketBase",
        "api_endpoints": {
            "/health": "Liveness probe (always 200)",
            "/ready": "Readiness probe (PocketBase reachable)",
            "/status": "Current OSINT processing job status",
            "/process": "POST to start a new OSINT processing job"
        }
    })

@app.route('/health')
def health_check():
    """Liveness check endpoint for Coolify."""
    return jsonify({"status": "ok"}), 200

@app.route('/ready')
def ready_check():
    """Readiness check: verifies PocketBase reachability."""
    try:
        is_ok = bool(pb_client and pb_client.health_check())
    except Exception:
        is_ok = False
    return jsonify({
        "ready": is_ok,
        "database": "reachable" if is_ok else "unreachable"
    }), (200 if is_ok else 503)

@app.route('/status')
def get_status():
    """Returns the current OSINT processing job status."""
    return jsonify(processing_status)

@app.route('/process', methods=['POST'])
def start_processing():
    """Starts a new OSINT processing job."""
    global processing_status
    if processing_status['status'] == 'running':
        return jsonify({"error": "A processing job is already running."}), 409

    data = request.get_json() or {}
    num_leads = data.get('num_leads', 10)  # Default to 10 leads for testing
    job_id = f"osint-job-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    config = get_config()

    # Start the processing in a new thread
    thread = threading.Thread(target=run_osint_processing, args=(job_id, config, num_leads))
    thread.daemon = True
    thread.start()

    return jsonify({
        "message": f"OSINT processing job '{job_id}' started.",
        "job_id": job_id,
        "num_leads": num_leads,
        "max_workers": config.processing.max_workers,
        "status_endpoint": "/status"
    }), 202

if __name__ == '__main__':
    config = get_config()
    app.run(host='0.0.0.0', port=config.server.port, threaded=True)
