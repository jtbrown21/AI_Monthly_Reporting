"""
Configuration settings for SF Domain Reports application.
"""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""
    
    # Airtable settings
    AIRTABLE_API_KEY: str
    AIRTABLE_BASE_ID: str

    # GitHub settings
    GITHUB_TOKEN: str
    GITHUB_REPO: str

    # Fields with default values
    AIRTABLE_REPORTS_TABLE: str = "My SF Domain Reports"
    AIRTABLE_KEYWORD_PERF_TABLE: str = "Keyword Performance"
    GITHUB_BRANCH: str = "main"
    GITHUB_REPORTS_PATH: str = "reports"
    PORT: int = 5000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables."""
        return cls(
            AIRTABLE_API_KEY=os.environ.get('AIRTABLE_API_KEY', ''),
            AIRTABLE_BASE_ID=os.environ.get('AIRTABLE_BASE_ID', ''),
            GITHUB_TOKEN=os.environ.get('GITHUB_TOKEN', ''),
            GITHUB_REPO=os.environ.get('GITHUB_REPO', ''),
            AIRTABLE_REPORTS_TABLE=os.environ.get('AIRTABLE_REPORTS_TABLE', 'My SF Domain Reports'),
            AIRTABLE_KEYWORD_PERF_TABLE=os.environ.get('AIRTABLE_KEYWORD_PERF_TABLE', 'Keyword Performance'),
            GITHUB_BRANCH=os.environ.get('GITHUB_BRANCH', 'main'),
            GITHUB_REPORTS_PATH=os.environ.get('GITHUB_REPORTS_PATH', 'reports'),
            PORT=int(os.environ.get('PORT', 5000)),
            DEBUG=os.environ.get('DEBUG', 'False').lower() == 'true',
            LOG_LEVEL=os.environ.get('LOG_LEVEL', 'INFO')
        )
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.AIRTABLE_API_KEY:
            errors.append("AIRTABLE_API_KEY is required")
        if not self.AIRTABLE_BASE_ID:
            errors.append("AIRTABLE_BASE_ID is required")
        if not self.GITHUB_TOKEN:
            errors.append("GITHUB_TOKEN is required")
        if not self.GITHUB_REPO:
            errors.append("GITHUB_REPO is required")
        if '/' not in self.GITHUB_REPO:
            errors.append("GITHUB_REPO must be in format 'username/repo'")
            
        return errors


# Global config instance
config = Config.from_env()