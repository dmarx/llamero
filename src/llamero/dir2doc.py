from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger
from jinja2 import Environment, FileSystemLoader
from .utils import load_config, get_project_root, commit_and_push


def get_ordered_templates(template_dir: Path, order_config: Optional[Dict[str, int]] = None) -> List[str]:
    """Get all templates in proper order.
    
    Args:
        template_dir: Path to template directory containing sections/
        order_config: Optional dictionary mapping filenames to order priority
        
    Returns:
        List of template names in desired order
    """
    sections_dir = template_dir / "sections"
    if not sections_dir.exists():
        sections_dir = template_dir  # Use template_dir itself if no sections/ subdirectory
        
    templates = []
    
    # Collect all template files
    for file in sections_dir.glob("*.j2"):
        if order_config and file.name in order_config and not file.exists():
            continue  # Skip optional files that don't exist
        templates.append(file.name)
    
    if order_config:
        # Sort by explicit order, then alphabetically for any new sections
        return sorted(
            templates,
            key=lambda x: order_config.get(x, 500)
        )
    else:
        # Just sort alphabetically if no order specified
        return sorted(templates)


def compile_template_dir(
    template_dir: Path,
    output_path: Optional[Path] = None,
    variables: Optional[Dict] = None,
    order_config: Optional[Dict[str, int]] = None,
    commit: bool = True
) -> None:
    """Compile a directory of templates into a single output file.
    
    Args:
        template_dir: Path to template directory
        output_path: Optional explicit output path. If None, uses directory name
        variables: Optional variables to pass to template rendering
        order_config: Optional dictionary defining template ordering
        commit: Whether to commit and push changes
    """
    project_root = get_project_root()
    logger.debug(f"Project root identified as: {project_root}")
    
    # Determine output path if not specified
    if output_path is None:
        output_name = template_dir.name.upper() + '.md'  # e.g. readme -> README.md
        output_path = project_root / output_name
    
    logger.info(f"Compiling templates from {template_dir} to {output_path}")
    
    # Load default variables from project config if none provided
    if variables is None:
        logger.info("Loading configurations")
        project_config = load_config("pyproject.toml")
        variables = {
            'project': project_config['project'],
            'config': project_config.get('tool', {}).get(template_dir.name, {})
        }
    
    logger.info("Setting up Jinja2 environment")
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    # Add template utility functions
    env.globals['get_ordered_templates'] = lambda: get_ordered_templates(template_dir, order_config)
    
    # Check for base template, fallback to concatenation if none exists
    try:
        template = env.get_template('base.md.j2')
        logger.info("Rendering using base template")
        output = template.render(**variables)
    except:
        logger.info("No base template found, concatenating section templates")
        templates = get_ordered_templates(template_dir, order_config)
        sections = []
        for template_name in templates:
            template = env.get_template(f"sections/{template_name}")
            sections.append(template.render(**variables))
        output = '\n\n'.join(sections)
    
    logger.debug(f"Writing output to: {output_path}")
    output_path.write_text(output)
    
    if commit:
        logger.info("Committing changes")
        commit_and_push(output_path)


def generate_readme() -> None:
    """Legacy function to maintain backwards compatibility"""
    template_dir = get_project_root() / 'docs/readme'
    section_order = {
        "introduction.md.j2": 0,
        "prerequisites.md.j2": 1,
        "usage.md.j2": 2,
        "development.md.j2": 3,
        "summaries.md.j2": 4,
        "site.md.j2": 5,
        "structure.md.j2": 6,
        "todo.md.j2": 999  # Always last if present
    }
    compile_template_dir(template_dir, order_config=section_order)


if __name__ == "__main__":
    generate_readme()
