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
        self.base_url = os.getenv('POCKETBASE_URL', 'https://pocketbase.ignitabull.org')
        # Service user credentials (Option B)
        self.user_email = os.getenv('POCKETBASE_SERVICE_EMAIL') or os.getenv('POCKETBASE_EMAIL', '')
        self.user_password = os.getenv('POCKETBASE_SERVICE_PASSWORD') or os.getenv('POCKETBASE_PASSWORD', '')

        # Admin credentials (fallback only if admin API is available)
        self.admin_email = os.getenv('POCKETBASE_ADMIN_EMAIL', self.user_email)
        self.admin_password = os.getenv('POCKETBASE_ADMIN_PASSWORD', self.user_password)

        self.auth_token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({'content-type': 'application/json'})

        # Collections
        self.leads_collection = 'leads'
        self.osint_results_collection = 'osint_results'
        self.processing_status_collection = 'processing_status'

    # -------------------- Auth --------------------
    def authenticate(self) -> bool:
        """Authenticate with PocketBase (user first, then admin fallback)."""
        # Try user auth (preferred)
        if self.user_email and self.user_password:
            try:
                url = f"{self.base_url}/api/collections/users/auth-with-password"
                payload = {"identity": self.user_email, "password": self.user_password}
                resp = self.session.post(url, data=json.dumps(payload), timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    token = data.get('token')
                    if token:
                        self.auth_token = token
                        self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                        logger.info("Authenticated to PocketBase as service user")
                        return True
            except Exception as e:
                logger.warning(f"User auth failed: {e}")

        # Fallback to admin auth (some deployments block admin API externally)
        try:
            url = f"{self.base_url}/api/admins/auth-with-password"
            payload = {"identity": self.admin_email, "password": self.admin_password}
            resp = self.session.post(url, data=json.dumps(payload), timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                token = data.get('token')
                if token:
                    self.auth_token = token
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    logger.info("Authenticated to PocketBase as admin")
                    return True
        except Exception as e:
            logger.warning(f"Admin auth failed: {e}")

        logger.error("PocketBase authentication unsuccessful (user and admin)")
        return False

    def ensure_authenticated(self) -> None:
        """Authenticate if not already authenticated."""
        if not self.auth_token:
            self.authenticate()

    # -------------------- Health --------------------
    def health_check(self) -> bool:
        try:
            resp = self.session.get(f"{self.base_url}/api/health", timeout=10)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"PocketBase health check failed: {e}")
            return False

    # -------------------- CRUD helpers --------------------
    def _post(self, collection: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/api/collections/{collection}/records"
        try:
            self.ensure_authenticated()
            resp = self.session.post(url, data=json.dumps(payload), timeout=20)
            if resp.status_code == 401:
                # Retry once after re-auth
                self.auth_token = None
                self.session.headers.pop('Authorization', None)
                self.ensure_authenticated()
                resp = self.session.post(url, data=json.dumps(payload), timeout=20)
            if resp.ok:
                return resp.json()
            else:
                logger.error(f"POST {collection} failed: {resp.status_code} {resp.text}")
                return None
        except Exception as e:
            logger.error(f"POST {collection} error: {e}")
            return None

    def _get(self, collection: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/collections/{collection}/records"
        try:
            self.ensure_authenticated()
            resp = self.session.get(url, params=params or {}, timeout=20)
            if resp.status_code == 401:
                # Retry once after re-auth
                self.auth_token = None
                self.session.headers.pop('Authorization', None)
                self.ensure_authenticated()
                resp = self.session.get(url, params=params or {}, timeout=20)
            if resp.ok:
                data = resp.json()
                return data.get('items', [])
            else:
                logger.error(f"GET {collection} failed: {resp.status_code} {resp.text}")
                return []
        except Exception as e:
            logger.error(f"GET {collection} error: {e}")
            return []

    # -------------------- Public API --------------------
    def create_lead(self, lead_data: Dict[str, Any]) -> Optional[str]:
        # Minimal field set for compatibility
        payload = {
            "email": lead_data.get("email"),
            "company": lead_data.get("company"),
            "country": lead_data.get("country"),
            "source": lead_data.get("source", "service")
        }
        res = self._post(self.leads_collection, payload)
        return res.get('id') if res else None

    def create_osint_result(self, result_data: Dict[str, Any]) -> Optional[str]:
        # Store enrichment details in a single JSON/text field for schema safety
        payload = {
            "lead_id": result_data.get("lead_id"),
            "email": result_data.get("email"),
            "company": result_data.get("company"),
            "country": result_data.get("country"),
            "score": result_data.get("score", 0),
            "status": result_data.get("status", "completed"),
            "processing_time": result_data.get("processing_time", 0),
            "enrichment_json": json.dumps(result_data.get("enrichment_data", {}), ensure_ascii=False)
        }
        res = self._post(self.osint_results_collection, payload)
        return res.get('id') if res else None

    def update_processing_status(self, status_data: Dict[str, Any]) -> Optional[str]:
        payload = {
            "job_id": status_data.get("job_id"),
            "status": status_data.get("status"),
            "total_leads": status_data.get("total_leads", 0),
            "processed_leads": status_data.get("processed_leads", 0),
            "successful_leads": status_data.get("successful_leads", 0),
            "failed_leads": status_data.get("failed_leads", 0),
            "average_score": status_data.get("average_score", 0),
            "total_processing_time": status_data.get("total_processing_time", 0),
            "updated": datetime.utcnow().isoformat()
        }
        res = self._post(self.processing_status_collection, payload)
        return res.get('id') if res else None

    def get_leads(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._get(self.leads_collection, params={'perPage': limit})

    def get_osint_results(self, lead_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {'perPage': limit}
        if lead_id:
            params['filter'] = f'lead_id = "{lead_id}"'
        return self._get(self.osint_results_collection, params=params)

    def get_processing_status(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {'perPage': 100}
        if job_id:
            params['filter'] = f'job_id = "{job_id}"'
        return self._get(self.processing_status_collection, params=params)
