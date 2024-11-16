# tests/test_summary/test_concatenative.py
from pathlib import Path
import pytest
from llamero.summary.concatenative import SummaryGenerator

def test_summary_generator_init(temp_project_dir):
    """Test SummaryGenerator initialization."""
    generator = SummaryGenerator(temp_project_dir)
    assert generator.root_dir == temp_project_dir

def test_should_include_file(temp_project_dir):
    """Test file inclusion logic."""
    generator = SummaryGenerator(temp_project_dir)
    
    # Should include
    assert generator.should_include_file(Path("test.py"))
    assert generator.should_include_file(Path("test.md"))
    assert generator.should_include_file(Path("test.toml"))
    
    # Should exclude
    assert not generator.should_include_file(Path(".git/config"))
    assert not generator.should_include_file(Path("__pycache__/test.pyc"))
    assert not generator.should_include_file(Path(".github/workflows/test.yml"))

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
