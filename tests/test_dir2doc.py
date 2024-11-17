from pathlib import Path
import pytest
from llamero.dir2doc import collect_section_templates, compile_template_dir

def test_collect_section_templates(temp_project_dir):
    """Test template collection and ordering."""
    template_dir = temp_project_dir / "templates"
    template_dir.mkdir()
    sections_dir = template_dir / "sections"
    sections_dir.mkdir()
    
    # Create test templates
    templates = ["b.md.j2", "a.md.j2", "c.md.j2"]
    for t in templates:
        (sections_dir / t).write_text("")
    
    # Test default ordering (alphabetical)
    ordered = collect_section_templates(sections_dir)
    assert ordered == sorted(templates)
    
    # Test explicit ordering
    order_config = {
        "c.md.j2": 1,
        "a.md.j2": 2,
        "b.md.j2": 3
    }
    ordered = collect_section_templates(sections_dir, order_config)
    assert ordered == ["c.md.j2", "a.md.j2", "b.md.j2"]
    
    # Test handling of templates not in order config
    (sections_dir / "d.md.j2").write_text("")
    ordered = collect_section_templates(sections_dir, order_config)
    assert "d.md.j2" not in ordered
    
    # Test empty order config
    ordered = collect_section_templates(sections_dir, {})
    assert len(ordered) == 4  # All templates included
    assert ordered == sorted([*templates, "d.md.j2"])

def test_compile_template_dir_with_base(temp_project_dir):
    """Test template compilation with base template."""
    template_dir = temp_project_dir / "templates"
    template_dir.mkdir()
    sections_dir = template_dir / "sections"
    sections_dir.mkdir()
    
    # Create test templates
    base_template = """# {{ project.name }}

{% for template in templates %}
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

def test_compile_template_dir_without_base(temp_project_dir):
    """Test template compilation without base template (fallback mode)."""
    template_dir = temp_project_dir / "templates"
    template_dir.mkdir()
    sections_dir = template_dir / "sections"
    sections_dir.mkdir()
    
    # Create test templates
    templates = {
        "a.md.j2": "## First Section\nThis is first.",
        "b.md.j2": "## Second Section\nThis is second.",
    }
    
    for name, content in templates.items():
        (sections_dir / name).write_text(content)
    
    # Test compilation
    output_path = temp_project_dir / "OUTPUT.md"
    compile_template_dir(
        template_dir,
        output_path=output_path,
        commit=False
    )
    
    # Check output
    output = output_path.read_text()
    assert "## First Section" in output
    assert "## Second Section" in output
    assert "This is first" in output
    assert "This is second" in output

def test_compile_template_dir_with_ordering(temp_project_dir):
    """Test template compilation with explicit ordering."""
    template_dir = temp_project_dir / "templates"
    template_dir.mkdir()
    sections_dir = template_dir / "sections"
    sections_dir.mkdir()
    
    # Create test templates
    templates = {
        "b.md.j2": "## Second\nShould appear second",
        "a.md.j2": "## First\nShould appear first",
    }
    
    for name, content in templates.items():
        (sections_dir / name).write_text(content)
    
    # Test compilation with ordering
    order_config = {
        "a.md.j2": 1,
        "b.md.j2": 2,
    }
    
    output_path = temp_project_dir / "OUTPUT.md"
    compile_template_dir(
        template_dir,
        output_path=output_path,
        order_config=order_config,
        commit=False
    )
    
    # Check output maintains order
    output = output_path.read_text()
    first_pos = output.find("Should appear first")
    second_pos = output.find("Should appear second")
    assert first_pos < second_pos
