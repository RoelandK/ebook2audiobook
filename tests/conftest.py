import os, sys, tempfile
import pytest

# Add project root to path so imports work
_proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _proj)


@pytest.fixture
def tmp_env():
    """Creates a temporary directory with a .env file and patches lib.conf._env_path."""
    import lib.conf as conf

    with tempfile.TemporaryDirectory() as td:
        orig = conf._env_path
        conf._env_path = os.path.join(td, ".env")
        yield td
        conf._env_path = orig
