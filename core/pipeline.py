#!/usr/bin/env python3
"""
Enhanced OSINT Enrichment Pipeline v2.0
Integrates Advanced Scoring Engine and Lead Prioritization
Based on 2024-2025 Industry Best Practices
"""

import json
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import subprocess

# Import our enhanced modules
from advanced_scoring import AdvancedScoringEngine
from lead_prioritization import LeadPrioritizationEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedOSINTPipeline:
    """
    Enhanced OSINT enrichment pipeline with advanced scoring and prioritization
    """
    
    def __init__(self):
        self.scoring_engine = AdvancedScoringEngine()
        self.prioritization_engine = LeadPrioritizationEngine()
        logger.info("Enhanced OSINT Pipeline v2.0 initialized")
    
    def enrich_lead_with_advanced_scoring(self, lead_data: Dict) -> Dict:
        """
        Enrich a single lead using the enhanced scoring engine
        """
        try:
            email = lead_data.get('email')
            if not email:
                logger.error("No email provided for enrichment")
                return lead_data
            
            logger.info(f"Starting enhanced enrichment for: {email}")
            
            # Extract existing enrichment data
            holehe_results = lead_data.get('holehe_results', {})
            domain_intelligence = lead_data.get('domain_intelligence', {})
            
            # Determine email provider
            email_provider = self._determine_email_provider(email)
            
            # Calculate enterprise-grade score
            scoring_result = self.scoring_engine.calculate_enterprise_score(
                holehe_results=holehe_results,
                domain_intelligence=domain_intelligence,
                email_provider=email_provider
            )
            
            # Update lead data with enhanced scoring
            lead_data.update({
                'enrichment_score': scoring_result.get('final_score', 0),
                'score_category': scoring_result.get('score_category', 'Unknown'),
                'business_intelligence': scoring_result.get('business_intelligence', {}),
                'scoring_details': scoring_result.get('component_scores', {}),
                'scoring_metadata': scoring_result.get('scoring_metadata', {}),
                'last_enriched_at': datetime.now().isoformat()
            })
            
            # Prioritize the lead
            prioritization_result = self.prioritization_engine.prioritize_lead(lead_data)
            lead_data['prioritization'] = prioritization_result
            
            logger.info(f"Enhanced enrichment completed for {email}: Score {scoring_result.get('final_score', 0)}")
            return lead_data
            
        except Exception as e:
            logger.error(f"Error in enhanced enrichment for {email}: {e}")
            lead_data['enrichment_error'] = str(e)
            return lead_data
    
    def _determine_email_provider(self, email: str) -> str:
        """Determine email provider for scoring calculations"""
        domain = email.split('@')[1].lower() if '@' in email else ''
        
        if domain in ['gmail.com']:
            return 'Gmail'
        elif domain in ['yahoo.com', 'yahoo.co.uk', 'yahoo.ca']:
            return 'Yahoo'
        elif domain in ['hotmail.com', 'hotmail.co.uk', 'outlook.com', 'live.com']:
            return 'Hotmail/Outlook'
        elif domain in ['gmx.com', 'gmx.de', 'gmx.ch']:
            return 'GMX'
        elif domain in ['yandex.ru', 'yandex.com']:
            return 'Yandex'
        elif domain in ['example.com', 'test.com']:
            return 'Test/Example'
        else:
            return 'Custom Domain'
    
    def process_leads_batch(self, leads_data: List[Dict], batch_size: int = 10) -> List[Dict]:
        """
        Process leads in batches with enhanced enrichment
        """
        logger.info(f"Processing {len(leads_data)} leads in batches of {batch_size}")
        
        enriched_leads = []
        total_leads = len(leads_data)
        
        for i in range(0, total_leads, batch_size):
            batch = leads_data[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_leads + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} leads)")
            
            for j, lead in enumerate(batch):
                lead_num = i + j + 1
                logger.info(f"Enriching lead {lead_num}/{total_leads}: {lead.get('email', 'Unknown')}")
                
                # Enhanced enrichment
                enriched_lead = self.enrich_lead_with_advanced_scoring(lead)
                enriched_leads.append(enriched_lead)
                
                # Progress update
                if (j + 1) % 5 == 0 or j == len(batch) - 1:
                    logger.info(f"Batch {batch_num} progress: {j + 1}/{len(batch)} leads processed")
                
                # Rate limiting (be respectful to APIs)
                time.sleep(0.1)
            
            logger.info(f"Batch {batch_num} completed. Total processed: {len(enriched_leads)}/{total_leads}")
        
        logger.info(f"All {total_leads} leads processed with enhanced enrichment")
        return enriched_leads
    
    def generate_enrichment_report(self, enriched_leads: List[Dict]) -> Dict:
        """
        Generate comprehensive enrichment report
        """
        try:
            total_leads = len(enriched_leads)
            if total_leads == 0:
                return {"error": "No leads to analyze"}
            
            # Score distribution analysis
            score_distribution = {}
            tier_distribution = {}
            business_priority_distribution = {}
            business_categories = {}
            
            total_score = 0
            successful_enrichments = 0
            
            for lead in enriched_leads:
                # Score analysis
                score = lead.get('enrichment_score', 0)
                if score > 0:
                    successful_enrichments += 1
                    total_score += score
                    
                    # Score category distribution
                    score_category = lead.get('score_category', 'Unknown')
                    score_distribution[score_category] = score_distribution.get(score_category, 0) + 1
                    
                    # Tier distribution
                    prioritization = lead.get('prioritization', {})
                    if prioritization and 'prioritization_summary' in prioritization:
                        tier = prioritization['prioritization_summary'].get('lead_tier', 'unknown')
                        tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
                        
                        business_priority = prioritization['prioritization_summary'].get('business_priority', 'unknown')
                        business_priority_distribution[business_priority] = business_priority_distribution.get(business_priority, 0) + 1
                
                # Business category analysis
                business_intel = lead.get('business_intelligence', {})
                if business_intel and 'primary_category' in business_intel:
                    category = business_intel['primary_category'].get('category', 'unknown')
                    business_categories[category] = business_categories.get(category, 0) + 1
            
            # Calculate averages
            avg_score = total_score / successful_enrichments if successful_enrichments > 0 else 0
            success_rate = (successful_enrichments / total_leads) * 100 if total_leads > 0 else 0
            
            # Top performing leads
            top_leads = sorted(enriched_leads, key=lambda x: x.get('enrichment_score', 0), reverse=True)[:10]
            top_leads_summary = []
            
            for lead in top_leads:
                top_leads_summary.append({
                    'email': lead.get('email'),
                    'score': lead.get('enrichment_score', 0),
                    'category': lead.get('score_category', 'Unknown'),
                    'tier': lead.get('prioritization', {}).get('prioritization_summary', {}).get('lead_tier', 'unknown')
                })
            
            report = {
                'enrichment_summary': {
                    'total_leads': total_leads,
                    'successful_enrichments': successful_enrichments,
                    'success_rate_percentage': round(success_rate, 2),
                    'average_enrichment_score': round(avg_score, 2),
                    'processing_timestamp': datetime.now().isoformat()
                },
                'score_distribution': score_distribution,
                'tier_distribution': tier_distribution,
                'business_priority_distribution': business_priority_distribution,
                'business_categories': business_categories,
                'top_performing_leads': top_leads_summary,
                'report_metadata': {
                    'report_version': '2.0.0',
                    'generated_by': 'Enhanced OSINT Pipeline',
                    'algorithm_version': '2.0.0'
                }
            }
            
            logger.info(f"Enrichment report generated: {successful_enrichments}/{total_leads} leads successfully enriched")
            return report
            
        except Exception as e:
            logger.error(f"Error generating enrichment report: {e}")
            return {"error": str(e)}
    
    def export_enriched_data(self, enriched_leads: List[Dict], format_type: str = 'json') -> str:
        """
        Export enriched data in various formats
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_type.lower() == 'json':
                filename = f"enriched_leads_{timestamp}.json"
                
                # Clean data for JSON export (remove non-serializable objects)
                clean_leads = []
                for lead in enriched_leads:
                    clean_lead = lead.copy()
                    # Remove timedelta objects that can't be serialized
                    if 'prioritization' in clean_lead:
                        prioritization = clean_lead['prioritization'].copy()
                        if 'response_requirements' in prioritization:
                            response_req = prioritization['response_requirements'].copy()
                            if 'response_time_required' in response_req:
                                # Convert timedelta to string
                                if hasattr(response_req['response_time_required'], 'total_seconds'):
                                    response_req['response_time_required'] = str(response_req['response_time_required'])
                            prioritization['response_requirements'] = response_req
                        clean_lead['prioritization'] = prioritization
                    clean_leads.append(clean_lead)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(clean_leads, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Enriched data exported to {filename}")
                return filename
            
            elif format_type.lower() == 'csv':
                import csv
                filename = f"enriched_leads_{timestamp}.csv"
                
                # Define CSV headers
                headers = [
                    'id', 'email', 'enrichment_score', 'score_category', 'lead_tier',
                    'business_priority', 'overall_priority', 'primary_business_category',
                    'response_urgency', 'nurturing_level', 'action_items'
                ]
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    
                    for lead in enriched_leads:
                        row = {
                            'id': lead.get('id', ''),
                            'email': lead.get('email', ''),
                            'enrichment_score': lead.get('enrichment_score', 0),
                            'score_category': lead.get('score_category', ''),
                            'lead_tier': lead.get('prioritization', {}).get('prioritization_summary', {}).get('lead_tier', ''),
                            'business_priority': lead.get('prioritization', {}).get('prioritization_summary', {}).get('business_priority', ''),
                            'overall_priority': lead.get('prioritization', {}).get('prioritization_summary', {}).get('overall_priority', ''),
                            'primary_business_category': lead.get('business_intelligence', {}).get('primary_category', {}).get('category', ''),
                            'response_urgency': lead.get('prioritization', {}).get('response_requirements', {}).get('urgency_level', ''),
                            'nurturing_level': lead.get('prioritization', {}).get('nurturing_strategy', {}).get('contact_frequency', ''),
                            'action_items': '; '.join(lead.get('prioritization', {}).get('action_items', []))
                        }
                        writer.writerow(row)
                
                logger.info(f"Enriched data exported to {filename}")
                return filename
            
            else:
                logger.error(f"Unsupported export format: {format_type}")
                return ""
                
        except Exception as e:
            logger.error(f"Error exporting enriched data: {e}")
            return ""

# Example usage and testing
if __name__ == "__main__":
    # Initialize the enhanced pipeline
    pipeline = EnhancedOSINTPipeline()
    
    # Test data
    test_leads = [
        {
            'id': 1,
            'email': 'entrepreneur@business.com',
            'holehe_results': {
                'platforms': {
                    'linkedin.com': 'exists',
                    'shopify.com': 'exists',
                    'instagram.com': 'exists'
                },
                'confirmed_accounts': 3
            },
            'domain_intelligence': {
                'domain': 'business.com',
                'reputation_score': 85,
                'spf_record': 'v=spf1',
                'mx_records': ['mx1.business.com']
            }
        },
        {
            'id': 2,
            'email': 'developer@gmail.com',
            'holehe_results': {
                'platforms': {
                    'github.com': 'exists',
                    'stackoverflow.com': 'exists',
                    'linkedin.com': 'exists'
                },
                'confirmed_accounts': 3
            },
            'domain_intelligence': {
                'domain': 'gmail.com',
                'reputation_score': 95,
                'spf_record': 'v=spf1 include:_spf.google.com',
                'mx_records': ['gmail-smtp-in.l.google.com']
            }
        }
    ]
    
    print("🚀 Enhanced OSINT Pipeline v2.0 Test")
    print("=" * 50)
    
    # Process leads
    enriched_leads = pipeline.process_leads_batch(test_leads)
    
    # Generate report
    report = pipeline.generate_enrichment_report(enriched_leads)
    
    print("\n📊 Enrichment Report:")
    print(json.dumps(report, indent=2))
    
    # Export data
    export_file = pipeline.export_enriched_data(enriched_leads, 'json')
    print(f"\n💾 Data exported to: {export_file}")
    
    print("\n✅ Enhanced OSINT Pipeline test completed successfully!")
