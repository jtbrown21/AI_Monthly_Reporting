#!/usr/bin/env python3
"""
Test script to verify the configuration fix for GITHUB_REPORTS_PATH.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """Test that configuration loads properly with all default values."""
    print("Testing configuration loading...")
    
    try:
        from config.settings import config
        
        print("✓ Config loaded successfully")
        print(f"  GITHUB_REPORTS_PATH: '{config.GITHUB_REPORTS_PATH}'")
        print(f"  GITHUB_BRANCH: '{config.GITHUB_BRANCH}'")
        print(f"  AIRTABLE_REPORTS_TABLE: '{config.AIRTABLE_REPORTS_TABLE}'")
        print(f"  AIRTABLE_KEYWORD_PERF_TABLE: '{config.AIRTABLE_KEYWORD_PERF_TABLE}'")
        print(f"  PORT: {config.PORT}")
        print(f"  DEBUG: {config.DEBUG}")
        print(f"  LOG_LEVEL: '{config.LOG_LEVEL}'")
        
        # Check that GITHUB_REPORTS_PATH is not None or empty
        assert config.GITHUB_REPORTS_PATH is not None, "GITHUB_REPORTS_PATH should not be None"
        assert config.GITHUB_REPORTS_PATH != "", "GITHUB_REPORTS_PATH should not be empty"
        assert config.GITHUB_REPORTS_PATH == "reports", f"Expected 'reports', got '{config.GITHUB_REPORTS_PATH}'"
        
        print("✓ All configuration values are properly set")
        return True
        
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False

def test_github_service_initialization():
    """Test that GitHub service can be initialized with the config."""
    print("\nTesting GitHub service initialization...")
    
    try:
        from config.settings import config
        from src.services.github import GitHubService
        
        # Set minimal required env vars for testing
        test_token = os.environ.get('GITHUB_TOKEN', 'test_token')
        test_repo = os.environ.get('GITHUB_REPO', 'test_user/test_repo')
        
        if not test_token or test_token == 'test_token':
            print("⚠ No real GITHUB_TOKEN found, using mock values for structure test")
        
        # Try to initialize the service
        github_service = GitHubService(
            token=test_token,
            repo=test_repo,
            branch=config.GITHUB_BRANCH
        )
        
        print("✓ GitHub service initialized successfully")
        print(f"  Repository: {github_service.repo}")
        print(f"  Branch: {github_service.branch}")
        
        return True
        
    except Exception as e:
        print(f"✗ GitHub service initialization failed: {e}")
        return False

def test_upload_method_signature():
    """Test that the upload_report method can be called with our parameters."""
    print("\nTesting upload_report method signature...")
    
    try:
        from src.services.github import GitHubService
        import inspect
        
        # Get the method signature
        signature = inspect.signature(GitHubService.upload_report)
        print(f"✓ upload_report signature: {signature}")
        
        # Check that our parameters match
        expected_params = ['self', 'content', 'filename', 'path']
        actual_params = list(signature.parameters.keys())
        
        print(f"  Expected parameters: {expected_params}")
        print(f"  Actual parameters: {actual_params}")
        
        for param in expected_params:
            assert param in actual_params, f"Missing parameter: {param}"
        
        # Check default value for path
        path_param = signature.parameters.get('path')
        if path_param and path_param.default != inspect.Parameter.empty:
            print(f"  Default value for 'path': '{path_param.default}'")
        
        print("✓ Method signature is compatible")
        return True
        
    except Exception as e:
        print(f"✗ Method signature test failed: {e}")
        return False

def test_webhook_parameters():
    """Test the specific parameters that would be passed in the webhook."""
    print("\nTesting webhook parameter compatibility...")
    
    try:
        from config.settings import config
        
        # Simulate the webhook call parameters
        test_content = "<html><body>Test Report</body></html>"
        test_filename = "Test_Client_June-2025.html"
        test_path = config.GITHUB_REPORTS_PATH
        
        print(f"  Content length: {len(test_content)} characters")
        print(f"  Filename: '{test_filename}'")
        print(f"  Path: '{test_path}'")
        
        # Verify all parameters are valid
        assert test_content, "Content should not be empty"
        assert test_filename, "Filename should not be empty"
        assert test_path, "Path should not be empty"
        assert test_path is not None, "Path should not be None"
        
        print("✓ All webhook parameters are valid")
        return True
        
    except Exception as e:
        print(f"✗ Webhook parameter test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING CONFIGURATION FIX")
    print("=" * 60)
    
    tests = [
        test_config_loading,
        test_github_service_initialization,
        test_upload_method_signature,
        test_webhook_parameters
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! The configuration fix should resolve the webhook error.")
    else:
        print("❌ Some tests failed. Please check the output above for details.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
