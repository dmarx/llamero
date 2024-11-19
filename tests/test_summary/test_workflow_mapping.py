# tests/test_summary/test_workflow_mapping.py
import pytest
from pathlib import Path
from llamero.summary.concatenative import SummaryGenerator

def test_directory_mapping(temp_project_dir):
    """Test that .github/workflows maps to github/workflows."""
    generator = SummaryGenerator(temp_project_dir)
    
    # Test workflow directory mapping
    original = Path(".github/workflows")
    mapped = generator._map_directory(original)
    # We want just the mapped path without the root directory
    mapped_relative = mapped.relative_to(generator.root_dir) if mapped.is_absolute() else mapped
    assert str(mapped_relative) == "github/workflows"
    
    # Test that other directories aren't affected
    normal_dir = Path("src/llamero")
    mapped_normal = generator._map_directory(normal_dir)
    mapped_normal_relative = mapped_normal.relative_to(generator.root_dir) if mapped_normal.is_absolute() else mapped_normal
    assert str(mapped_normal_relative) == str(normal_dir)

def test_workflow_summary_generation(temp_project_dir):
    """Test generation of workflow summaries in mapped location."""
    # Create workflow dir and file
    workflow_dir = temp_project_dir / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    
    workflow_content = """
name: Test Workflow
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
"""
    (workflow_dir / "test.yml").write_text(workflow_content)
    
    # Generate summaries
    generator = SummaryGenerator(temp_project_dir)
    summary_files = generator.generate_all_summaries()
    
    # Check that summary was created in mapped location
    mapped_summary = temp_project_dir / "github" / "workflows" / "SUMMARY"
    assert mapped_summary in summary_files
    assert mapped_summary.exists()
    
    # Verify content
    content = mapped_summary.read_text()
    assert "File: .github/workflows/test.yml" in content

def test_mixed_directory_handling(temp_project_dir):
    """Test handling of both workflow and non-workflow directories."""
    # Create workflow file
    workflow_dir = temp_project_dir / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "test.yml").write_text("name: Test")
    
    # Create regular file
    src_dir = temp_project_dir / "src" / "llamero"
    src_dir.mkdir(parents=True)
    (src_dir / "test.py").write_text("print('test')")
    
    # Generate summaries
    generator = SummaryGenerator(temp_project_dir)
    summary_files = generator.generate_all_summaries()
    
    # Check both summaries
    workflow_summary = temp_project_dir / "github" / "workflows" / "SUMMARY"
    src_summary = src_dir / "SUMMARY"
    
    assert workflow_summary in summary_files
    assert workflow_summary.exists()
    assert src_summary in summary_files
    assert src_summary.exists()
