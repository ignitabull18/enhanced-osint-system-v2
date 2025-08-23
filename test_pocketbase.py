#!/usr/bin/env python3
"""
Test script for PocketBase connection and collections
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.pocketbase_client import PocketBaseClient

def test_pocketbase_connection():
    """Test PocketBase connection and basic operations"""
    print("🧪 Testing PocketBase Connection")
    print("=" * 40)
    
    try:
        # Initialize client
        print("📡 Initializing PocketBase client...")
        client = PocketBaseClient()
        
        # Test authentication
        print("🔐 Testing authentication...")
        if client.authenticate():
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed!")
            return False
        
        # Test health check
        print("🏥 Testing health check...")
        if client.health_check():
            print("✅ Health check passed!")
        else:
            print("❌ Health check failed!")
            return False
        
        # Test creating a test lead
        print("📝 Testing lead creation...")
        test_lead = {
            'email': 'test@example.com',
            'name': 'Test User',
            'company': 'Test Company',
            'source': 'test_script'
        }
        
        lead_id = client.create_lead(test_lead)
        if lead_id:
            print(f"✅ Lead created successfully! ID: {lead_id}")
        else:
            print("❌ Failed to create lead!")
            return False
        
        # Test creating OSINT result
        print("🔍 Testing OSINT result creation...")
        test_result = {
            'lead_id': lead_id,
            'email': 'test@example.com',
            'osint_score': 85,
            'findings': {
                'social_media': ['twitter', 'linkedin'],
                'breaches': 0,
                'domain_info': 'example.com'
            }
        }
        
        result_id = client.create_osint_result(test_result)
        if result_id:
            print(f"✅ OSINT result created successfully! ID: {result_id}")
        else:
            print("❌ Failed to create OSINT result!")
            return False
        
        # Test creating processing status
        print("📊 Testing processing status creation...")
        test_status = {
            'job_id': 'test_job_123',
            'status': 'completed',
            'batch_size': 100,
            'max_workers': 10,
            'start_time': '2025-01-23T18:00:00Z',
            'end_time': '2025-01-23T18:05:00Z'
        }
        
        status_id = client.update_processing_status(test_status)
        if status_id:
            print(f"✅ Processing status created successfully! ID: {status_id}")
        else:
            print("❌ Failed to create processing status!")
            return False
        
        # Test retrieving data
        print("📥 Testing data retrieval...")
        leads = client.get_leads(limit=10)
        print(f"✅ Retrieved {len(leads)} leads")
        
        results = client.get_osint_results(limit=10)
        print(f"✅ Retrieved {len(results)} OSINT results")
        
        statuses = client.get_processing_status()
        print(f"✅ Retrieved {len(statuses)} processing status records")
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pocketbase_connection()
    sys.exit(0 if success else 1)
