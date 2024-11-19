# tests/test_summary/test_concatenative.py
from pathlib import Path
import pytest
from llamero.summary.concatenative import SummaryGenerator

def test_summary_generator_init(temp_project_dir):
    """Test SummaryGenerator initialization."""
    generator = SummaryGenerator(temp_project_dir)
    assert generator.root_dir == temp_project_dir

# tests/test_summary/test_concatenative.py

def test_should_include_file(temp_project_dir, monkeypatch):
    """Test file inclusion logic."""
    # Change to temp directory so it's treated as project root
    monkeypatch.chdir(temp_project_dir)
    
    # Create some test files
    test_py = temp_project_dir / "test.py"
    test_md = temp_project_dir / "test.md"
    test_yaml = temp_project_dir / "test.yml"
    test_bin = temp_project_dir / "test.bin"
    excluded = temp_project_dir / ".git" / "config"
    
    # Write small content to each file
    for file in [test_py, test_md, test_yaml, test_bin]:
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("test content")
    
    excluded.parent.mkdir(parents=True, exist_ok=True)
    excluded.write_text("test content")
    
    generator = SummaryGenerator(temp_project_dir)
    
    # Should include
    assert generator.should_include_file(test_py)
    assert generator.should_include_file(test_md)
    assert generator.should_include_file(test_yaml)
    
    # Should exclude
    assert not generator.should_include_file(test_bin)  # Wrong extension
    assert not generator.should_include_file(excluded)  # In .git directory

def test_generate_directory_summary(temp_project_dir):
    """Test directory summary generation."""
    generator = SummaryGenerator(temp_project_dir)
    summary = generator.generate_directory_summary(temp_project_dir)
    
    # Check that summary contains expected files
    assert "File: pyproject.toml" in summary
    assert "File: README.md" in summary
    assert "# Test Project" in summary

def test_generate_all_summaries(temp_project_dir):
    """Test generation of all summaries."""
    generator = SummaryGenerator(temp_project_dir)
    summary_files = generator.generate_all_summaries()
    
    # Check that summaries were generated
    assert len(summary_files) > 0
    assert all(f.name == "SUMMARY" for f in summary_files)
    
    # Check content of root summary
    root_summary = (temp_project_dir / "SUMMARY").read_text()
    assert "File: pyproject.toml" in root_summary
    assert "File: README.md" in root_summary
