# tests/conftest.py
import pytest
from pathlib import Path
import tempfile
import shutil
import os

@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory with a pyproject.toml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create minimal pyproject.toml
        pyproject_content = """
[project]
name = "test-project"
description = "Test project"
version = "0.1.0"
requires-python = ">=3.11"

[tool.llamero]
verbose = true
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content)
        
        # Create some test files and directories
        src_dir = tmp_path / "src" / "test_project"
        src_dir.mkdir(parents=True)
        
        # Sample Python file
        (src_dir / "main.py").write_text("""
def hello():
    \"\"\"Say hello.\"\"\"
    return "Hello, world!"

class TestClass:
    \"\"\"A test class.\"\"\"
    def method(self):
        \"\"\"A test method.\"\"\"
        return True
""")
        
        # Sample README
        (tmp_path / "README.md").write_text("# Test Project\n\nThis is a test.")
        
        yield tmp_path

@pytest.fixture
def mock_git_repo(temp_project_dir):
    """Create a temporary git repository."""
    os.chdir(temp_project_dir)
    os.system("git init")
    os.system("git config user.name 'Test User'")
    os.system("git config user.email 'test@example.com'")
    os.system("git add .")
    os.system("git commit -m 'Initial commit'")
    yield temp_project_dir
    os.chdir(os.path.dirname(temp_project_dir))

