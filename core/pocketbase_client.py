"""
PocketBase Client for Enhanced OSINT System v2.0
Handles database operations for leads, OSINT results, and processing status
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class PocketBaseClient:
    """Client for interacting with PocketBase database"""
    
    def __init__(self):
        """Initialize PocketBase client with configuration"""
        self.base_url = os.getenv('POCKETBASE_URL', 'https://pocketbase.ignitabull.org')
        self.email = os.getenv('POCKETBASE_EMAIL', 'jeremy@ignitabull.com')
        self.password = os.getenv('POCKETBASE_PASSWORD', 'Negroid18!')
        self.auth_token = None
        self.session = requests.Session()
        
        # Collection names
        self.leads_collection = 'leads'
        self.osint_results_collection = 'osint_results'
        self.processing_status_collection = 'processing_status'
        
        # Authenticate on initialization
        self.authenticate()
    
    def authenticate(self) -> bool:
        """Authenticate with PocketBase and get auth token"""
        try:
            auth_url = f"{self.base_url}/api/admins/auth-with-password"
            auth_data = {
                "identity": self.email,
                "password": self.password
            }
            
            response = self.session.post(auth_url, json=auth_data)
            response.raise_for_status()
            
            auth_response = response.json()
            self.auth_token = auth_response.get('token')
            
            if self.auth_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                logger.info("Successfully authenticated with PocketBase")
                return True
            else:
                logger.error("No auth token received from PocketBase")
                return False
                
        except Exception as e:
            logger.error(f"Failed to authenticate with PocketBase: {e}")
            return False
    
    def create_lead(self, lead_data: Dict[str, Any]) -> Optional[str]:
        """Create a new lead record"""
        try:
            url = f"{self.base_url}/api/collections/{self.leads_collection}/records"
            
            # Add timestamp
            lead_data['created'] = datetime.utcnow().isoformat()
            lead_data['updated'] = datetime.utcnow().isoformat()
            
            response = self.session.post(url, json=lead_data)
            response.raise_for_status()
            
            result = response.json()
            record_id = result.get('id')
            logger.info(f"Created lead record: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to create lead: {e}")
            return None
    
    def create_osint_result(self, result_data: Dict[str, Any]) -> Optional[str]:
        """Create a new OSINT result record"""
        try:
            url = f"{self.base_url}/api/collections/{self.osint_results_collection}/records"
            
            # Add timestamp
            result_data['created'] = datetime.utcnow().isoformat()
            result_data['updated'] = datetime.utcnow().isoformat()
            
            response = self.session.post(url, json=result_data)
            response.raise_for_status()
            
            result = response.json()
            record_id = result.get('id')
            logger.info(f"Created OSINT result record: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to create OSINT result: {e}")
            return None
    
    def update_processing_status(self, status_data: Dict[str, Any]) -> Optional[str]:
        """Create or update processing status record"""
        try:
            url = f"{self.base_url}/api/collections/{self.processing_status_collection}/records"
            
            # Add timestamp
            status_data['updated'] = datetime.utcnow().isoformat()
            
            response = self.session.post(url, json=status_data)
            response.raise_for_status()
            
            result = response.json()
            record_id = result.get('id')
            logger.info(f"Updated processing status: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to update processing status: {e}")
            return None
    
    def get_leads(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get leads from database"""
        try:
            url = f"{self.base_url}/api/collections/{self.leads_collection}/records"
            params = {'perPage': limit}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            leads = result.get('items', [])
            logger.info(f"Retrieved {len(leads)} leads from database")
            return leads
            
        except Exception as e:
            logger.error(f"Failed to retrieve leads: {e}")
            return []
    
    def get_osint_results(self, lead_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get OSINT results, optionally filtered by lead_id"""
        try:
            url = f"{self.base_url}/api/collections/{self.osint_results_collection}/records"
            params = {'perPage': limit}
            
            if lead_id:
                params['filter'] = f'lead_id = "{lead_id}"'
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            results = result.get('items', [])
            logger.info(f"Retrieved {len(results)} OSINT results from database")
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve OSINT results: {e}")
            return []
    
    def get_processing_status(self, job_id: str = None) -> List[Dict[str, Any]]:
        """Get processing status records, optionally filtered by job_id"""
        try:
            url = f"{self.base_url}/api/collections/{self.processing_status_collection}/records"
            params = {'perPage': 100}
            
            if job_id:
                params['filter'] = f'job_id = "{job_id}"'
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            statuses = result.get('items', [])
            logger.info(f"Retrieved {len(statuses)} processing status records from database")
            return statuses
            
        except Exception as e:
            logger.error(f"Failed to retrieve processing status: {e}")
            return []
    
    def health_check(self) -> bool:
        """Check if PocketBase is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"PocketBase health check failed: {e}")
            return False
