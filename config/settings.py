"""
Enhanced OSINT System v2.0 - Configuration Management
Centralized configuration for Coolify deployment
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str
    anon_key: str
    project_id: str = ""
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        return cls(
            url=os.getenv('SUPABASE_URL', ''),
            anon_key=os.getenv('SUPABASE_ANON_KEY', ''),
            project_id=os.getenv('SUPABASE_PROJECT_ID', '')
        )

@dataclass
class ProcessingConfig:
    """Processing configuration settings"""
    max_workers: int
    batch_size: int
    timeout_seconds: int
    retry_attempts: int
    
    @classmethod
    def from_env(cls) -> 'ProcessingConfig':
        return cls(
            max_workers=int(os.getenv('MAX_WORKERS', '80')),
            batch_size=int(os.getenv('BATCH_SIZE', '5000')),
            timeout_seconds=int(os.getenv('TIMEOUT_SECONDS', '300')),
            retry_attempts=int(os.getenv('RETRY_ATTEMPTS', '3'))
        )

@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    level: str
    format: str
    file_path: str
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        return cls(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file_path=os.getenv('LOG_FILE', '/app/logs/osint.log')
        )

@dataclass
class OSINTConfig:
    """OSINT tool configuration settings"""
    holehe_timeout: int
    whois_timeout: int
    dns_timeout: int
    social_timeout: int
    
    @classmethod
    def from_env(cls) -> 'OSINTConfig':
        return cls(
            holehe_timeout=int(os.getenv('HOLEHE_TIMEOUT', '30')),
            whois_timeout=int(os.getenv('WHOIS_TIMEOUT', '30')),
            dns_timeout=int(os.getenv('DNS_TIMEOUT', '15')),
            social_timeout=int(os.getenv('SOCIAL_TIMEOUT', '20'))
        )

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.database = DatabaseConfig.from_env()
        self.processing = ProcessingConfig.from_env()
        self.logging = LoggingConfig.from_env()
        self.osint = OSINTConfig.from_env()
        
        # Environment
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Coolify specific
        self.coolify_instance = os.getenv('COOLIFY_INSTANCE', '')
        self.deployment_id = os.getenv('DEPLOYMENT_ID', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'database': {
                'url': self.database.url,
                'project_id': self.database.project_id
            },
            'processing': {
                'max_workers': self.processing.max_workers,
                'batch_size': self.processing.batch_size,
                'timeout_seconds': self.processing.timeout_seconds
            },
            'logging': {
                'level': self.logging.level,
                'file_path': self.logging.file_path
            },
            'environment': self.environment,
            'debug': self.debug
        }
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.database.url or not self.database.anon_key:
            print("❌ Missing Supabase credentials")
            return False
        
        if self.processing.max_workers <= 0:
            print("❌ Invalid max_workers value")
            return False
        
        if self.processing.batch_size <= 0:
            print("❌ Invalid batch_size value")
            return False
        
        print("✅ Configuration validated successfully")
        return True

# Global configuration instance
config = Config()

def get_config() -> Config:
    """Get global configuration instance"""
    return config
