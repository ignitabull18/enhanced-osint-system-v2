"""
Export module for sending enriched OSINT results to external systems.
"""

import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from termcolor import colored

logger = logging.getLogger(__name__)


class SupabaseExporter:
    """Export enriched leads to Supabase Ultra Scraper database."""
    
    def __init__(self):
        """Initialize Supabase exporter with credentials."""
        self.url = os.getenv('SUPABASE_URL', 'https://db.cndhtcpgcmqrvlypzooc.supabase.co')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY', '')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY', '')
        
        # Use service key if available, otherwise anon key
        self.api_key = self.service_key if self.service_key else self.anon_key
        
        if not self.api_key:
            logger.warning(colored("⚠️ No Supabase API key configured", "yellow"))
    
    def export_to_unified_leads(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Export enriched leads to the unified_leads table.
        
        Args:
            leads: List of enriched lead dictionaries
            
        Returns:
            Export result with success/failure counts
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'No Supabase API key configured',
                'exported': 0,
                'failed': 0
            }
        
        endpoint = f"{self.url}/rest/v1/unified_leads"
        headers = {
            'apikey': self.api_key,
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates'
        }
        
        exported = 0
        failed = 0
        errors = []
        
        # Process leads in batches of 100
        batch_size = 100
        for i in range(0, len(leads), batch_size):
            batch = leads[i:i+batch_size]
            
            # Transform leads to match unified_leads schema
            transformed_batch = []
            for lead in batch:
                transformed = self._transform_lead_for_unified(lead)
                if transformed:
                    transformed_batch.append(transformed)
            
            if not transformed_batch:
                continue
            
            try:
                # Upsert batch to Supabase
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=transformed_batch,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    exported += len(transformed_batch)
                    logger.info(colored(f"✅ Exported batch of {len(transformed_batch)} leads", "green"))
                else:
                    failed += len(transformed_batch)
                    error_msg = f"Batch export failed: {response.status_code} - {response.text}"
                    errors.append(error_msg)
                    logger.error(colored(f"❌ {error_msg}", "red"))
                    
            except Exception as e:
                failed += len(transformed_batch)
                error_msg = f"Export exception: {str(e)}"
                errors.append(error_msg)
                logger.error(colored(f"❌ {error_msg}", "red"))
        
        result = {
            'success': exported > 0,
            'exported': exported,
            'failed': failed,
            'total': len(leads)
        }
        
        if errors:
            result['errors'] = errors[:5]  # Keep first 5 errors
        
        return result
    
    def _transform_lead_for_unified(self, lead: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform PocketBase lead format to Supabase unified_leads format.
        
        Args:
            lead: Lead data from PocketBase
            
        Returns:
            Transformed lead or None if invalid
        """
        try:
            # Extract enrichment data
            enrichment = lead.get('enrichment_json', {})
            if isinstance(enrichment, str):
                try:
                    enrichment = json.loads(enrichment)
                except:
                    enrichment = {}
            
            # Build transformed lead
            transformed = {
                'email': lead.get('email'),
                'first_name': lead.get('first_name'),
                'last_name': lead.get('last_name'),
                'source_table': 'osint_enrichment',
                'original_id': lead.get('id'),
                'enrichment_status': 'enriched',
                'last_enriched_at': datetime.utcnow().isoformat()
            }
            
            # Add validation status
            validation = enrichment.get('validation', {})
            if validation:
                transformed['email_validation_status'] = validation.get('status', 'unknown')
            
            # Add domain intelligence
            domain_intel = enrichment.get('domain_analysis', {})
            if domain_intel:
                transformed['domain_intelligence'] = domain_intel
            
            # Add HOLEHE results
            holehe = enrichment.get('holehe', {})
            if holehe:
                transformed['holehe_results'] = holehe
            
            # Add enrichment score
            score = enrichment.get('enrichment_score', 0)
            transformed['enrichment_score'] = score
            
            # Add social profiles if found
            social = enrichment.get('social_profiles', {})
            if social:
                # Instagram
                if 'instagram' in social:
                    ig = social['instagram']
                    transformed['instagram_profile'] = ig.get('username')
                    transformed['instagram_bio'] = ig.get('bio')
                    transformed['instagram_followers'] = ig.get('followers')
                    transformed['instagram_following'] = ig.get('following')
                    transformed['instagram_posts'] = ig.get('posts')
                
                # Facebook
                if 'facebook' in social:
                    fb = social['facebook']
                    transformed['facebook_profile'] = fb.get('profile_url')
                    transformed['facebook_bio'] = fb.get('bio')
                    transformed['facebook_followers'] = fb.get('followers')
                    transformed['facebook_likes'] = fb.get('likes')
                
                # TikTok
                if 'tiktok' in social:
                    tt = social['tiktok']
                    transformed['tiktok_profile'] = tt.get('username')
                    transformed['tiktok_bio'] = tt.get('bio')
                    transformed['tiktok_followers'] = tt.get('followers')
                    transformed['tiktok_likes'] = tt.get('likes')
                
                # YouTube
                if 'youtube' in social:
                    yt = social['youtube']
                    transformed['youtube_channel'] = yt.get('channel_url')
                    transformed['youtube_bio'] = yt.get('bio')
                    transformed['youtube_subscribers'] = yt.get('subscribers')
                    transformed['youtube_videos'] = yt.get('videos')
            
            # Store any additional data
            transformed['additional_data'] = {
                'pocketbase_id': lead.get('id'),
                'enrichment_timestamp': lead.get('updated'),
                'raw_enrichment': enrichment
            }
            
            return transformed
            
        except Exception as e:
            logger.error(f"Failed to transform lead {lead.get('id')}: {str(e)}")
            return None


class PostJobExporter:
    """Main exporter that coordinates post-job exports to various systems."""
    
    def __init__(self, pb_client=None):
        """
        Initialize post-job exporter.
        
        Args:
            pb_client: PocketBase client instance
        """
        self.pb_client = pb_client
        self.supabase = SupabaseExporter()
        
    def export_completed_enrichments(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Export all completed enrichments to external systems.
        
        Args:
            job_id: Optional specific job ID to export
            
        Returns:
            Export results summary
        """
        print(colored("\n📤 Starting Post-Job Export...", "cyan", attrs=['bold']))
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'job_id': job_id,
            'fetched': 0,
            'supabase': {'exported': 0, 'failed': 0}
        }
        
        try:
            # Fetch completed enrichments from PocketBase
            enriched_leads = self._fetch_enriched_leads(job_id)
            results['fetched'] = len(enriched_leads)
            
            if not enriched_leads:
                print(colored("ℹ️ No enriched leads to export", "yellow"))
                return results
            
            print(colored(f"📊 Found {len(enriched_leads)} enriched leads to export", "cyan"))
            
            # Export to Supabase Ultra Scraper
            if self.supabase.api_key:
                print(colored("🚀 Exporting to Supabase Ultra Scraper...", "cyan"))
                supabase_result = self.supabase.export_to_unified_leads(enriched_leads)
                results['supabase'] = supabase_result
                
                if supabase_result['success']:
                    print(colored(
                        f"✅ Supabase Export: {supabase_result['exported']}/{supabase_result['total']} leads",
                        "green"
                    ))
                else:
                    print(colored(
                        f"⚠️ Supabase Export Issues: {supabase_result.get('error', 'Unknown error')}",
                        "yellow"
                    ))
            else:
                print(colored("⏭️ Skipping Supabase export (no API key)", "yellow"))
            
            # Summary
            print(colored("\n📈 Export Summary:", "cyan", attrs=['bold']))
            print(colored(f"  • Total Fetched: {results['fetched']}", "white"))
            print(colored(f"  • Supabase Exported: {results['supabase']['exported']}", "green"))
            if results['supabase']['failed'] > 0:
                print(colored(f"  • Supabase Failed: {results['supabase']['failed']}", "red"))
            
        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            results['error'] = error_msg
            print(colored(f"❌ {error_msg}", "red"))
            logger.error(error_msg, exc_info=True)
        
        return results
    
    def _fetch_enriched_leads(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch enriched leads from PocketBase.
        
        Args:
            job_id: Optional job ID to filter by
            
        Returns:
            List of enriched lead dictionaries
        """
        if not self.pb_client:
            logger.warning("No PocketBase client available")
            return []
        
        try:
            # Fetch leads with enrichment data
            endpoint = "/api/collections/osint_results/records"
            params = {
                'perPage': 500,
                'filter': 'enrichment_json != null && enrichment_json != ""'
            }
            
            # Add job filter if specified
            if job_id:
                params['filter'] += f' && job_id = "{job_id}"'
            
            response = self.pb_client._get(endpoint, params=params)
            
            if response and 'items' in response:
                leads = []
                
                # Combine lead and enrichment data
                for result in response['items']:
                    lead_data = {
                        'id': result.get('id'),
                        'lead_id': result.get('lead_id'),
                        'email': result.get('email'),
                        'first_name': result.get('first_name'),
                        'last_name': result.get('last_name'),
                        'enrichment_json': result.get('enrichment_json'),
                        'created': result.get('created'),
                        'updated': result.get('updated')
                    }
                    leads.append(lead_data)
                
                return leads
            
        except Exception as e:
            logger.error(f"Failed to fetch enriched leads: {str(e)}")
        
        return []


def run_post_job_export(pb_client=None, job_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to run post-job export.
    
    Args:
        pb_client: PocketBase client instance
        job_id: Optional job ID to export
        
    Returns:
        Export results
    """
    exporter = PostJobExporter(pb_client)
    return exporter.export_completed_enrichments(job_id)
