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
    assert str(mapped) == "github/workflows"
    
    # Test that other directories aren't affected
    normal_dir = Path("src/llamero")
    assert generator._map_directory(normal_dir) == normal_dir

def test_workflow_summary_generation(temp_project_dir):
    """Test generation of workflow summaries in mapped location."""
    # Create original workflow files
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
    
    # Verify content references original path
    summary_content = mapped_summary.read_text()
    assert "File: .github/workflows/test.yml" in summary_content
    assert "name: Test Workflow" in summary_content

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
    assert src_summary in summary_files
    
    # Verify content maintains correct paths
    workflow_content = workflow_summary.read_text()
    assert "File: .github/workflows/test.yml" in workflow_content
    
    src_content = src_summary.read_text()
    assert "File: src/llamero/test.py" in src_content
