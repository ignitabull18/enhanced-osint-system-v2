#!/usr/bin/env python3
"""
Enhanced OSINT System v2.0 - Coolify Deployment
Flask web service with PocketBase integration
"""

import os
import sys
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any
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
    'errors': []
}

# Initialize PocketBase client
pocketbase_client = None

def setup_logging(config: Config) -> None:
    """Setup logging configuration"""
    log_dir = Path(config.logging.file_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config.logging.level.upper()),
        format=config.logging.format,
        handlers=[
            logging.FileHandler(config.logging.file_path),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_osint_processing(batch_size: int, max_workers: int) -> None:
    """Run OSINT processing in background thread"""
    global processing_status
    
    try:
        processing_status['status'] = 'running'
        processing_status['start_time'] = datetime.utcnow().isoformat()
        processing_status['errors'] = []
        
        # Update processing status in PocketBase
        if pocketbase_client:
            pocketbase_client.update_processing_status({
                'job_id': f"osint_job_{int(time.time())}",
                'status': 'running',
                'batch_size': batch_size,
                'max_workers': max_workers,
                'start_time': processing_status['start_time']
            })
        
        # Run the OSINT processing
        process_real_leads_production_parallel(
            batch_size=batch_size,
            max_workers=max_workers
        )
        
        processing_status['status'] = 'completed'
        processing_status['end_time'] = datetime.utcnow().isoformat()
        
        # Update final status in PocketBase
        if pocketbase_client:
            pocketbase_client.update_processing_status({
                'job_id': f"osint_job_{int(time.time())}",
                'status': 'completed',
                'end_time': processing_status['end_time']
            })
            
    except Exception as e:
        processing_status['status'] = 'error'
        processing_status['end_time'] = datetime.utcnow().isoformat()
        processing_status['errors'].append(str(e))
        
        # Update error status in PocketBase
        if pocketbase_client:
            pocketbase_client.update_processing_status({
                'job_id': f"osint_job_{int(time.time())}",
                'status': 'error',
                'error_message': str(e),
                'end_time': processing_status['end_time']
            })

@app.route('/')
def index():
    """System information endpoint"""
    return jsonify({
        'system': 'Enhanced OSINT System v2.0',
        'version': '2.0.0',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'health': '/health',
            'status': '/status',
            'process': '/process'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for Coolify"""
    try:
        config = get_config()
        
        # Check PocketBase connection
        pocketbase_healthy = False
        if pocketbase_client:
            pocketbase_healthy = pocketbase_client.health_check()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "environment": config.environment,
            "pocketbase_connection": "connected" if pocketbase_healthy else "disconnected"
        })
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/status')
def status():
    """Get current processing status"""
    return jsonify(processing_status)

@app.route('/process', methods=['POST'])
def start_processing():
    """Start OSINT processing job"""
    global processing_status
    
    # Check if already processing
    if processing_status['status'] in ['running', 'starting']:
        return jsonify({
            'error': 'Processing already in progress',
            'current_status': processing_status
        }), 400
    
    try:
        data = request.get_json() or {}
        batch_size = data.get('batch_size', 1000)
        max_workers = data.get('max_workers', 80)
        
        # Validate parameters
        if batch_size <= 0 or max_workers <= 0:
            return jsonify({
                'error': 'Invalid parameters: batch_size and max_workers must be positive'
            }), 400
        
        # Start processing in background thread
        processing_status['current_job'] = f"osint_job_{int(time.time())}"
        processing_status['total_leads'] = batch_size
        processing_status['processed_leads'] = 0
        
        thread = threading.Thread(
            target=run_osint_processing,
            args=(batch_size, max_workers),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'message': 'OSINT processing started',
            'job_id': processing_status['current_job'],
            'batch_size': batch_size,
            'max_workers': max_workers,
            'status': 'started'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to start processing: {str(e)}'
        }), 500

def main():
    """Main application entry point"""
    global pocketbase_client
    
    print("🚀 Enhanced OSINT System v2.0 - Coolify Deployment")
    print("=" * 60)
    
    try:
        # Load configuration
        config = get_config()
        print(f"📋 Environment: {config.environment}")
        print(f"🔧 Max Workers: {config.processing.max_workers}")
        print(f"📊 Batch Size: {config.processing.batch_size}")
        
        # Setup logging
        setup_logging(config)
        logger = logging.getLogger(__name__)
        logger.info("Enhanced OSINT System starting up")
        
        # Initialize PocketBase client
        try:
            pocketbase_client = PocketBaseClient()
            if pocketbase_client.authenticate():
                print("✅ Connected to PocketBase successfully")
                logger.info("Connected to PocketBase successfully")
            else:
                print("⚠️ Failed to authenticate with PocketBase")
                logger.warning("Failed to authenticate with PocketBase")
        except Exception as e:
            print(f"⚠️ PocketBase connection failed: {e}")
            logger.warning(f"PocketBase connection failed: {e}")
            pocketbase_client = None
        
        # Start Flask app on port 8002
        print("🌐 Starting Flask web service on port 8002...")
        logger.info("Starting Flask web service on port 8002")
        
        app.run(
            host='0.0.0.0',
            port=8002,
            debug=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        logger.info("Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()