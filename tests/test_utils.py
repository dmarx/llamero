# tests/test_utils.py
import pytest
from pathlib import Path
import os
from llamero.utils import get_project_root, load_config

def test_get_project_root(temp_project_dir):
    """Test project root detection."""
    os.chdir(temp_project_dir)
    root = get_project_root()
    assert root == temp_project_dir
    assert (root / "pyproject.toml").exists()

def test_get_project_root_subfolder(temp_project_dir):
    """Test project root detection from subfolder."""
    subfolder = temp_project_dir / "src"
    os.chdir(subfolder)
    root = get_project_root()
    assert root == temp_project_dir

def test_load_config(temp_project_dir):
    """Test configuration loading."""
    os.chdir(temp_project_dir)
    config = load_config("pyproject.toml")
    assert config["project"]["name"] == "test-project"
    assert config["tool"]["llamero"]["verbose"] is True

def test_load_config_missing():
    """Test loading missing configuration."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.toml")
