# tests/test_summary/test_aggregation.py

import pytest
from pathlib import Path
from llamero.summary.concatenative import SummaryGenerator

def create_nested_summaries(root_dir: Path) -> dict[str, Path]:
    """Create a nested directory structure with SUMMARY files.
    
    Returns a dict mapping directory names to their Path objects.
    """
    # Create test structure:
    # root/
    #   |- frontend/
    #       |- src/
    #           |- js/
    #           |- styles/
    #           |- templates/
    
    paths = {}
    
    # Create directories
    frontend_dir = root_dir / "frontend"
    src_dir = frontend_dir / "src"
    js_dir = src_dir / "js"
    styles_dir = src_dir / "styles"
    templates_dir = src_dir / "templates"
    
    for dir_path in [frontend_dir, src_dir, js_dir, styles_dir, templates_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        paths[dir_path.name] = dir_path
    
    # Create some files in each leaf directory
    js_files = {
        "main.js": "console.log('main');",
        "utils.js": "export function util() {}"
    }
    
    styles_files = {
        "main.css": "body { color: black; }",
        "utils.css": ".util { display: none; }"
    }
    
    template_files = {
        "index.html": "<html><body></body></html>",
        "footer.html": "<footer></footer>"
    }
    
    # Write files and create initial summaries
    for dir_path, files in [
        (js_dir, js_files),
        (styles_dir, styles_files),
        (templates_dir, template_files)
    ]:
        for name, content in files.items():
            (dir_path / name).write_text(content)
    
    return paths

def test_basic_aggregation(temp_project_dir):
    """Test basic summary aggregation in a nested directory structure."""
    paths = create_nested_summaries(temp_project_dir)
    
    generator = SummaryGenerator(temp_project_dir)
    summary_files = generator.generate_all_summaries()
    
    # Check that summaries were created at each level
    assert (paths["frontend"] / "SUMMARY").exists()
    assert (paths["src"] / "SUMMARY").exists()
    assert (paths["js"] / "SUMMARY").exists()
    assert (paths["styles"] / "SUMMARY").exists()
    assert (paths["templates"] / "SUMMARY").exists()
    
    # Verify content format
    src_summary = (paths["src"] / "SUMMARY").read_text()
    frontend_summary = (paths["frontend"] / "SUMMARY").read_text()
    
    # Check that delimiters are preserved
    assert "---\nFile:" in src_summary
    assert "---\nFile:" in frontend_summary
    
    # Check that content is propagated up
    js_content = (paths["js"] / "SUMMARY").read_text()
    assert js_content in src_summary
    assert js_content in frontend_summary

def test_aggregation_with_empty_directories(temp_project_dir):
    """Test that empty directories don't affect aggregation."""
    paths = create_nested_summaries(temp_project_dir)
    
    # Add an empty directory
    empty_dir = paths["src"] / "empty"
    empty_dir.mkdir()
    
    generator = SummaryGenerator(temp_project_dir)
    generator.generate_all_summaries()
    
    src_summary = (paths["src"] / "SUMMARY").read_text()
    frontend_summary = (paths["frontend"] / "SUMMARY").read_text()
    
    # Empty directory should not affect content
    assert not (empty_dir / "SUMMARY").exists()
    assert src_summary == frontend_summary

def test_aggregation_formatting(temp_project_dir):
    """Test that aggregated summaries maintain correct formatting."""
    paths = create_nested_summaries(temp_project_dir)
    
    generator = SummaryGenerator(temp_project_dir)
    generator.generate_all_summaries()
    
    src_summary = (paths["src"] / "SUMMARY").read_text()
    
    # Check spacing between file sections
    sections = src_summary.split("---\nFile:")
    assert len(sections) > 1
    
    # First section is empty due to split
    for section in sections[1:]:
        # Each section should end with at least one newline
        assert section.strip().endswith("\n")
        # Verify section format
        assert "---" in section

def test_aggregation_content_preservation(temp_project_dir):
    """Test that all content is preserved during aggregation."""
    paths = create_nested_summaries(temp_project_dir)
    
    generator = SummaryGenerator(temp_project_dir)
    generator.generate_all_summaries()
    
    # Get all unique content from leaf SUMMARYs
    leaf_content = set()
    for dir_name in ["js", "styles", "templates"]:
        summary = (paths[dir_name] / "SUMMARY").read_text()
        leaf_content.update(line for line in summary.splitlines() if line.strip())
    
    # Check that all content appears in parent summaries
    src_summary = (paths["src"] / "SUMMARY").read_text()
    frontend_summary = (paths["frontend"] / "SUMMARY").read_text()
    
    for line in leaf_content:
        if line.strip():  # Skip empty lines
            assert line in src_summary
            assert line in frontend_summary

def test_aggregation_order(temp_project_dir):
    """Test that directory order is maintained in aggregated summaries."""
    paths = create_nested_summaries(temp_project_dir)
    
    generator = SummaryGenerator(temp_project_dir)
    generator.generate_all_summaries()
    
    src_summary = (paths["src"] / "SUMMARY").read_text()
    
    # Get positions of each subdirectory's content
    js_pos = src_summary.find("File: js/")
    styles_pos = src_summary.find("File: styles/")
    templates_pos = src_summary.find("File: templates/")
    
    # Verify directory order matches sorted order
    assert js_pos < styles_pos < templates_pos

def test_aggregation_with_excluded_directories(temp_project_dir):
    """Test that excluded directories don't affect aggregation."""
    paths = create_nested_summaries(temp_project_dir)
    
    # Create an excluded directory with content
    excluded_dir = paths["src"] / "__pycache__"
    excluded_dir.mkdir()
    (excluded_dir / "cache.pyc").write_text("cache content")
    
    generator = SummaryGenerator(temp_project_dir)
    generator.generate_all_summaries()
    
    src_summary = (paths["src"] / "SUMMARY").read_text()
    
    # Verify excluded content is not present
    assert "cache content" not in src_summary
    assert "__pycache__" not in src_summary
