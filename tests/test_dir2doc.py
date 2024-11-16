# tests/test_dir2doc.py
from pathlib import Path
import pytest
from llamero.dir2doc import get_ordered_templates, compile_template_dir

def test_get_ordered_templates(temp_project_dir):
    """Test template ordering."""
    template_dir = temp_project_dir / "templates"
    template_dir.mkdir()
    (template_dir / "sections").mkdir()
    
    # Create test templates
    templates = ["b.md.j2", "a.md.j2", "c.md.j2"]
    for t in templates:
        (template_dir / "sections" / t).write_text("")
    
    # Test default ordering (alphabetical)
    ordered = get_ordered_templates(template_dir)
    assert ordered == sorted(templates)
    
    # Test explicit ordering
    order_config = {
        "c.md.j2": 1,
        "a.md.j2": 2,
        "b.md.j2": 3
    }
    ordered = get_ordered_templates(template_dir, order_config)
    assert ordered == ["c.md.j2", "a.md.j2", "b.md.j2"]


def test_compile_template_dir(temp_project_dir):
    """Test template compilation."""
    template_dir = temp_project_dir / "templates"
    template_dir.mkdir()
    sections_dir = template_dir / "sections"
    sections_dir.mkdir()
    
    # Create test templates
    base_template = """# {{ project.name }}

{% for template in get_ordered_templates() %}
{%- include "sections/" ~ template %}
{% endfor %}"""
    (template_dir / "base.md.j2").write_text(base_template)
    
    section_template = """## Section
This is a test section."""
    (sections_dir / "test.md.j2").write_text(section_template)
    
    # Test compilation
    output_path = temp_project_dir / "OUTPUT.md"
    compile_template_dir(
        template_dir,
        output_path=output_path,
        variables={"project": {"name": "Test Project"}},
        commit=False
    )
    
    # Check output
    output = output_path.read_text()
    assert "# Test Project" in output
    assert "## Section" in output
    assert "This is a test section." in output
