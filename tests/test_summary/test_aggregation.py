# tests/test_summary/test_aggregation.py

import pytest
from pathlib import Path
from llamero.summary.concatenative import SummaryGenerator

def create_nested_summaries(root_dir: Path) -> dict[str, Path]:
    """Create a nested directory structure with SUMMARY files."""
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
    
    # Create test files with their base paths properly included in the content
    js_files = {
        "main.js": {
            "content": "console.log('main');",
            "path": "frontend/src/js/main.js"
        },
        "utils.js": {
            "content": "export function util() {}",
            "path": "frontend/src/js/utils.js"
        }
    }
    
    styles_files = {
        "main.css": {
            "content": "body { color: black; }",
            "path": "frontend/src/styles/main.css"
        },
        "utils.css": {
            "content": ".util { display: none; }",
            "path": "frontend/src/styles/utils.css"
        }
    }
    
    template_files = {
        "index.html": {
            "content": "<html><body></body></html>",
            "path": "frontend/src/templates/index.html"
        },
        "footer.html": {
            "content": "<footer></footer>",
            "path": "frontend/src/templates/footer.html"
        }
    }
    
    # Write files
    for dir_name, files in [
        ("js", js_files),
        ("styles", styles_files),
        ("templates", template_files)
    ]:
        dir_path = paths[dir_name]
        for name, file_info in files.items():
            file_path = dir_path / name
            file_path.write_text(file_info["content"])
            
            # Create SUMMARY content with proper file paths
            summary_content = []
            summary_content.extend([
                "---",
                f"File: {file_info['path']}",
                "---",
                file_info["content"],
                "\n"
            ])
            
            # Write SUMMARY for each directory
            (dir_path / "SUMMARY").write_text("\n".join(summary_content))
    
    return paths
    
def test_aggregation_formatting(temp_project_dir):
    """Test that aggregated summaries maintain correct formatting."""
    paths = create_nested_summaries(temp_project_dir)
    
    generator = SummaryGenerator(temp_project_dir)
    generator.generate_all_summaries()
    
    src_summary = (paths["src"] / "SUMMARY").read_text()
    
    # Check proper section formatting
    sections = src_summary.split("---")
    for section in sections[1:]:  # Skip first empty section
        # Each section should follow format: \nFile: path\n---\ncontent\n
        lines = section.splitlines()
        assert lines[0].startswith("File: "), f"Section doesn't start with 'File: ': {lines[0]}"
        
        # Check section structure
        content = "\n".join(lines[1:])
        assert content.strip(), "Section content is empty"
        assert section.endswith("\n"), "Section doesn't end with newline"

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
