import os
import sys

# Ensure repository root is on sys.path (tests already do this elsewhere)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_config_defaults():
    # Import the package-local config
    from skynet.config import Config as PackageConfig

    c = PackageConfig()
    assert hasattr(c, 'ollama_model')
    assert hasattr(c, 'search_provider')
    assert c.ollama_model != ''

def test_top_level_shim():
    # Also verify the package-local import works as a sanity check
    from skynet.config import Config as ShimConfig

    c = ShimConfig()
    assert hasattr(c, 'ollama_model')
    assert hasattr(c, 'search_provider')
