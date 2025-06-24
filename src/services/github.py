"""
GitHub service for uploading reports to GitHub Pages.
"""
import base64
import requests
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for GitHub operations."""
    
    def __init__(self, token: str, repo: str, branch: str = "main"):
        """
        Initialize GitHub service.
        
        Args:
            token: GitHub personal access token
            repo: Repository in format "username/repo"
            branch: Target branch (default: main)
        """
        self.token = token
        self.repo = repo
        self.branch = branch
        self.api_base = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Parse username and repo name
        parts = repo.split('/')
        if len(parts) != 2:
            raise ValueError("Repository must be in format 'username/repo'")
        
        self.username = parts[0]
        self.repo_name = parts[1]
        
        logger.info(f"Initialized GitHub service for {repo}")
    
    def upload_report(
        self, 
        content: str, 
        filename: str, 
        path: str = "reports"
    ) -> str:
        """
        Upload HTML report to GitHub repository.
        
        Args:
            content: HTML content to upload
            filename: Name of the file
            path: Directory path in repository
            
        Returns:
            GitHub Pages URL for the uploaded file
        """
        try:
            # Ensure filename is safe
            safe_filename = self._sanitize_filename(filename)
            
            # Create full path
            file_path = f"{path}/{safe_filename}"
            
            # Encode content to base64
            content_bytes = content.encode('utf-8')
            content_base64 = base64.b64encode(content_bytes).decode('utf-8')
            
            # Check if file already exists
            existing_sha = self._get_file_sha(file_path)
            
            # Prepare API request
            url = f"{self.api_base}/repos/{self.repo}/contents/{file_path}"
            
            data = {
                'message': f'Add report: {safe_filename}',
                'content': content_base64,
                'branch': self.branch
            }
            
            # Include SHA if updating existing file
            if existing_sha:
                data['sha'] = existing_sha
                data['message'] = f'Update report: {safe_filename}'
            
            # Make request
            response = requests.put(url, json=data, headers=self.headers)
            
            if response.status_code not in [201, 200]:
                logger.error(f"GitHub API error: {response.status_code} - {response.text}")
                raise Exception(f"Failed to upload to GitHub: {response.status_code}")
            
            # Generate GitHub Pages URL
            # Use custom domain instead of github.io
            pages_url = f"https://app.agentinsider.co/{file_path}"
            logger.info(f"Successfully uploaded report to: {pages_url}")
            return pages_url
            
        except Exception as e:
            logger.error(f"Error uploading to GitHub: {str(e)}")
            raise
    
    def _get_file_sha(self, file_path: str) -> Optional[str]:
        """
        Get SHA of existing file if it exists.
        
        Args:
            file_path: Path to file in repository
            
        Returns:
            SHA string or None if file doesn't exist
        """
        try:
            url = f"{self.api_base}/repos/{self.repo}/contents/{file_path}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json().get('sha')
            
            return None
            
        except Exception as e:
            logger.debug(f"File doesn't exist or error getting SHA: {e}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe storage.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace unsafe characters
        safe = filename.replace(' ', '_').replace('/', '_')
        
        # Ensure .html extension
        if not safe.endswith('.html'):
            safe += '.html'
        
        return safe
    
    def create_directory_structure(self, paths: list[str]) -> bool:
        """
        Ensure directory structure exists in repository.
        
        Args:
            paths: List of directory paths to create
            
        Returns:
            True if successful
        """
        try:
            for path in paths:
                # Create a README in each directory to ensure it exists
                readme_content = f"# {path.capitalize()} Directory\n\nThis directory contains generated reports."
                readme_path = f"{path}/README.md"
                
                # Check if README already exists
                if not self._get_file_sha(readme_path):
                    self.upload_report(readme_content, "README.md", path)
                    logger.info(f"Created directory: {path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating directory structure: {e}")
            return False