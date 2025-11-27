import os
import sys
from unittest.mock import patch
import pytest


@pytest.fixture(autouse=True)
def setup_test_mode():
    """Set up test mode to redirect session replay to test file."""
    # Set environment variable to indicate test mode
    os.environ['TEST_MODE'] = '1'
    
    # Patch the main module to use test session replay file
    original_main = sys.modules.get('src.main')
    if 'src.main' in sys.modules:
        # If main module is already loaded, modify its attributes
        main_module = sys.modules['src.main']
        if hasattr(main_module, 'EventManagerApp'):
            # Temporarily store the original __init__ method
            original_init = main_module.EventManagerApp.__init__
            
            def new_init(self):
                # Call original init
                original_init(self)
                # Override session replay file for tests
                self.session_replay_file = "session_replay_test.txt"
                self.is_test_mode = True
            
            main_module.EventManagerApp.__init__ = new_init
    
    yield
    
    # Cleanup after test
    if 'TEST_MODE' in os.environ:
        del os.environ['TEST_MODE']