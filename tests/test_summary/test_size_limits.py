# tests/test_summary/test_size_limits.py
import pytest
from pathlib import Path
import os
from llamero.summary.concatenative import SummaryGenerator

def test_file_size_threshold_config(temp_project_dir, monkeypatch):
    """Test that size threshold is properly loaded from config."""
    # Change to temp directory so it's treated as project root
    monkeypatch.chdir(temp_project_dir)
    
    # Update pyproject.toml with size threshold
    config_content = """
[project]
name = "test-project"
description = "Test project"
version = "0.1.0"

[tool.summary]
max_file_size_kb = 10  # 10KB threshold
"""
    (temp_project_dir / "pyproject.toml").write_text(config_content)
    
    generator = SummaryGenerator(temp_project_dir)
    assert generator.max_file_size == 10 * 1024  # Should be converted to bytes

def test_file_size_filtering(temp_project_dir, monkeypatch):
    """Test that files are filtered based on size."""
    # Change to temp directory so it's treated as project root
    monkeypatch.chdir(temp_project_dir)
    
    # Set up config with 1KB threshold
    config_content = """
[project]
name = "test-project"
description = "Test project"
version = "0.1.0"

[tool.summary]
max_file_size_kb = 1  # 1KB threshold
"""
    (temp_project_dir / "pyproject.toml").write_text(config_content)
    
    # Create test files
    small_file = temp_project_dir / "small.py"
    large_file = temp_project_dir / "large.py"
    
    # 500 bytes file (under threshold)
    small_file.write_text("x" * 500)
    
    # 2KB file (over threshold)
    large_file.write_text("x" * 2048)
    
    generator = SummaryGenerator(temp_project_dir)
    
    # Test individual file inclusion
    assert generator.should_include_file(small_file)
    assert not generator.should_include_file(large_file)

def test_directory_summary_with_size_limit(temp_project_dir, monkeypatch):
    """Test that directory summaries respect size limits."""
    # Change to temp directory so it's treated as project root
    monkeypatch.chdir(temp_project_dir)
    
    # Set up config with 1KB threshold
    config_content = """
[project]
name = "test-project"
description = "Test project"
version = "0.1.0"

[tool.summary]
max_file_size_kb = 1
"""
    (temp_project_dir / "pyproject.toml").write_text(config_content)
    
    # Create test files in a subdirectory
    test_dir = temp_project_dir / "test_dir"
    test_dir.mkdir()
    
    small_file = test_dir / "small.py"
    large_file = test_dir / "large.py"
    
    small_content = "def small_function():\n    pass"
    large_content = "x" * 2048  # 2KB of content
    
    small_file.write_text(small_content)
    large_file.write_text(large_content)
    
    generator = SummaryGenerator(temp_project_dir)
    summary = generator.generate_directory_summary(test_dir)
    
    # Summary should include small file but not large file
    assert "small.py" in summary
    assert "small_function" in summary
    assert "large.py" not in summary
    assert large_content not in summary

# def test_size_limit_warning_logging(temp_project_dir, monkeypatch, caplog):
#     """Test that appropriate warnings are logged for skipped files."""
#     # Change to temp directory so it's treated as project root
#     monkeypatch.chdir(temp_project_dir)
#     caplog.set_level("WARNING")
    
#     # Set up config with 1KB threshold
#     config_content = """
# [project]
# name = "test-project"
# description = "Test project"
# version = "0.1.0"

# [tool.summary]
# max_file_size_kb = 1
# """
#     (temp_project_dir / "pyproject.toml").write_text(config_content)
    
#     # Create a large file
#     large_file = temp_project_dir / "large.py"
#     large_file.write_text("x" * 2048)  # 2KB
    
#     generator = SummaryGenerator(temp_project_dir)
#     generator.generate_directory_summary(temp_project_dir)
    
#     # Check that a warning was logged
#     assert any([
#         "Skipping large file" in record.message and "large.py" in record.message
#         for record in caplog.records
#     ])
