from loguru import logger
from pathlib import Path
import pytest
from llamero.tree_generator import (
    should_include_path,
    node_to_tree,
    generate_tree
)

@pytest.fixture
def mock_repo_with_files(mock_git_repo):
    """Extend mock_git_repo with additional test files"""
    # Add workflow files
    workflow_dir = mock_git_repo / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "test.yml").write_text("name: Test")
    (workflow_dir / "build.yml").write_text("name: Build")
    
    # Add various hidden files
    (mock_git_repo / ".env").write_text("SECRET=123")
    (mock_git_repo / ".github" / "README.md").write_text("# GitHub Config")
    
    # Add some regular files and directories
    docs_dir = mock_git_repo / "docs" / "readme" / "sections"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "introduction.md").write_text("# Intro")
    
    # Add some files that should typically be ignored
    cache_dir = mock_git_repo / "__pycache__"
    cache_dir.mkdir(exist_ok=True)
    (cache_dir / "module.pyc").write_text("cache")
    
    return mock_git_repo

def test_ignore_patterns(mock_git_repo):
    """Test that ignore patterns work correctly"""
    config = {
        "tool": {
            "readme": {
                "tree": {
                    "ignore_patterns": [".git", "__pycache__", "*.pyc"]
                }
            }
        }
    }
    
    # Should exclude based on exact pattern matches
    assert not should_include_path(Path(".git/config"), config)
    assert not should_include_path(Path("foo/__pycache__/bar.pyc"), config)
    assert not should_include_path(Path("test.pyc"), config)
    
    # Should include non-matching paths
    assert should_include_path(Path(".github/workflows/test.yml"), config)
    assert should_include_path(Path(".env"), config)
    assert should_include_path(Path("docs/readme/file.md"), config)
    assert should_include_path(Path("src/test_project/main.py"), config)

def test_full_tree_generation(mock_repo_with_files, monkeypatch):
    """Test complete tree generation with various file types"""
    monkeypatch.chdir(mock_repo_with_files)
    
    # Update existing pyproject.toml with tree config
    config_content = """
[project]
name = "test-project"
description = "Test project"
version = "0.1.0"
requires-python = ">=3.11"

[tool.llamero]
verbose = true

[tool.readme.tree]
ignore_patterns = ["__pycache__", "*.pyc", ".git"]
"""
    (mock_repo_with_files / "pyproject.toml").write_text(config_content)
    
    tree = generate_tree(".")
    print(f"Generated tree:\n{tree}")  # Keep for debugging
    
    tree_lines = tree.splitlines()
    
    # Should include .github and workflows
    assert any(".github" in line for line in tree_lines)
    assert any("workflows" in line for line in tree_lines)
    assert any("test.yml" in line for line in tree_lines)
    assert any("build.yml" in line for line in tree_lines)
    
    # Should include other files from mock_git_repo
    assert any("src" in line for line in tree_lines)
    assert any("test_project" in line for line in tree_lines)
    assert any("main.py" in line for line in tree_lines)
    
    # Should include added test files
    assert any(".env" in line for line in tree_lines)
    assert any("docs" in line for line in tree_lines)
    assert any("readme" in line for line in tree_lines)
    assert any("sections" in line for line in tree_lines)
    
    # Should exclude ignored patterns - check each line individually
    assert not any(line.strip().endswith("__pycache__") for line in tree_lines)
    assert not any(line.strip().endswith(".git") for line in tree_lines)
    assert not any(line.endswith(".pyc") for line in tree_lines)

def test_empty_directory_handling(mock_git_repo):
    """Test handling of empty directories"""
    # Create some empty directories
    (mock_git_repo / "docs" / "empty").mkdir(parents=True, exist_ok=True)
    (mock_git_repo / "src" / "empty").mkdir(parents=True, exist_ok=True)
    (mock_git_repo / "temp" / "empty").mkdir(parents=True, exist_ok=True)
    
    config = {
        "tool": {
            "readme": {
                "tree": {
                    "ignore_patterns": []
                }
            }
        }
    }
    
    # Empty directories should be excluded unless they're essential
    assert node_to_tree(mock_git_repo / "temp" / "empty", config) is None
    
    # Essential directories should be kept even if empty
    assert node_to_tree(mock_git_repo / "docs", config) is not None
    assert node_to_tree(mock_git_repo / "src", config) is not None

def test_debug_path_processing(mock_repo_with_files):
    """Debug test to print path processing details"""
    config = {
        "tool": {
            "readme": {
                "tree": {
                    "ignore_patterns": ["__pycache__", "*.pyc"]
                }
            }
        }
    }
    
    def debug_walk(path: Path, indent=""):
        logger.debug(f"{indent}Processing: {path}")
        logger.debug(f"{indent}Should include: {should_include_path(path, config)}")
        
        if path.is_dir():
            for child in sorted(path.iterdir()):
                debug_walk(child, indent + "  ")
    
    logger.debug("Starting debug walk of repository")
    debug_walk(mock_repo_with_files)
