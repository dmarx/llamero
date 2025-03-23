# tests/test_config.py
import pytest
from pathlib import Path
import os
import yaml
import shutil
from llamero.config import (
    load_config, create_default_config, create_llameroignore,
    get_pattern_spec, should_include_path, read_ignore_file
)

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary directory for config tests."""
    # Create test directory structure
    test_dir = tmp_path / "config_test"
    test_dir.mkdir()
    
    # Save current working directory
    old_cwd = os.getcwd()
    
    # Change to test directory
    os.chdir(test_dir)
    
    yield test_dir
    
    # Restore original working directory
    os.chdir(old_cwd)

def test_create_default_config(temp_config_dir):
    """Test creation of default config file."""
    config_path = create_default_config()
    
    assert config_path.exists()
    assert config_path.name == ".llamero.yml"
    
    # Check that the config is valid YAML
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Verify basic structure
    assert "summary" in config
    assert "max_file_size_kb" in config["summary"]
    assert isinstance(config["summary"]["max_file_size_kb"], int)

def test_create_llameroignore(temp_config_dir):
    """Test creation of default .llameroignore file."""
    ignore_path = create_llameroignore()
    
    assert ignore_path.exists()
    assert ignore_path.name == ".llameroignore"
    
    # Check content
    content = ignore_path.read_text()
    assert ".git/" in content
    assert "# Llamero ignore file" in content
    assert "!.git/config" in content  # Example of negation

def test_load_config_no_files(temp_config_dir):
    """Test loading config with no config files present."""
    config = load_config()
    
    # Should have defaults
    assert "summary" in config
    assert "max_file_size_kb" in config["summary"]
    assert config["summary"].get("max_file_size_kb") == 1000
    
    # Should have minimal exclude pattern for .git
    assert "exclude_patterns" in config["summary"]
    assert ".git/" in config["summary"]["exclude_patterns"]

def test_load_config_with_config(temp_config_dir):
    """Test loading config with a .llamero.yml file."""
    # Create a config file
    config_file = temp_config_dir / ".llamero.yml"
    with open(config_file, 'w') as f:
        f.write("""
summary:
  max_file_size_kb: 2000
  custom_value: test
        """)
    
    config = load_config()
    
    # Should merge with defaults
    assert config["summary"]["max_file_size_kb"] == 2000
    assert config["summary"]["custom_value"] == "test"
    assert "exclude_patterns" in config["summary"]

def test_load_config_with_ignore_file(temp_config_dir):
    """Test loading config with a .llameroignore file."""
    # Create an ignore file
    ignore_file = temp_config_dir / ".llameroignore"
    with open(ignore_file, 'w') as f:
        f.write("""
# Custom ignore patterns
*.log
node_modules/
!important.log
        """)
    
    config = load_config()
    
    # Should include patterns from ignore file
    patterns = config["summary"]["exclude_patterns"]
    assert "*.log" in patterns
    assert "node_modules/" in patterns
    assert "!important.log" in patterns

def test_get_pattern_spec():
    """Test creating pattern spec from patterns."""
    patterns = [".git/", "*.log", "node_modules/"]
    spec = get_pattern_spec(patterns)
    
    # Test matching
    assert spec.match_file(".git/config")  # Should match
    assert spec.match_file("logs/app.log")  # Should match
    assert not spec.match_file("src/app.py")  # Should not match

def test_should_include_path():
    """Test path inclusion logic."""
    patterns = [".git/", "*.log", "node_modules/", "!important.log"]
    spec = get_pattern_spec(patterns)
    
    # Setup paths
    root = Path("/project")
    git_file = Path("/project/.git/config")
    log_file = Path("/project/logs/app.log")
    important_log = Path("/project/important.log")
    python_file = Path("/project/src/app.py")
    
    # Test inclusion/exclusion
    assert not should_include_path(git_file, spec, root)  # Should be excluded
    assert not should_include_path(log_file, spec, root)  # Should be excluded
    assert should_include_path(python_file, spec, root)   # Should be included
    
    # Test negation pattern
    assert should_include_path(important_log, spec, root) # Should be included due to negation

def test_read_ignore_file_fallback(temp_config_dir):
    """Test fallback to .gitignore if no .llameroignore exists."""
    # Create a .gitignore file
    gitignore = temp_config_dir / ".gitignore"
    with open(gitignore, 'w') as f:
        f.write("""
# Git ignore patterns
*.pyc
__pycache__/
        """)
    
    patterns = read_ignore_file()
    
    assert "*.pyc" in patterns
    assert "__pycache__/" in patterns

def test_read_ignore_file_priority(temp_config_dir):
    """Test that .llameroignore takes priority over .gitignore."""
    # Create both files
    llameroignore = temp_config_dir / ".llameroignore"
    with open(llameroignore, 'w') as f:
        f.write("llamero_pattern")
    
    gitignore = temp_config_dir / ".gitignore"
    with open(gitignore, 'w') as f:
        f.write("git_pattern")
    
    patterns = read_ignore_file()
    
    # Should use .llameroignore
    assert "llamero_pattern" in patterns
    assert "git_pattern" not in patterns
