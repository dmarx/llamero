from pathlib import Path
from typing import Dict
from loguru import logger
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from .utils import load_config, get_project_root, commit_and_push

def collect_section_templates(sections_dir: Path, order_config: dict | None = None) -> list[str]:
    """
    Collect and order section templates from a directory.
    
    Args:
        sections_dir: Directory containing section templates
        order_config: Optional mapping of template names to order values from config
        
    Returns:
        List of template names in correct order
    """
    templates = []
    for file in sections_dir.glob("*.j2"):
        if not order_config or file.name in order_config:
            templates.append(file.name)
    
    return sorted(templates, key=lambda x: order_config.get(x, 500) if order_config else x)

def compile_template_dir(
    template_dir: Path,
    output_path: Path | None = None,
    variables: Dict | None = None,
    order_config: Dict | None = None,
    commit: bool = True
) -> None:
    """
    Compile a directory of templates into a single output file.
    
    Args:
        template_dir: Path to template directory
        output_path: Optional explicit output path. If None, uses directory name
        variables: Optional variables to pass to template rendering
        order_config: Optional dictionary defining template ordering
        commit: Whether to commit and push changes
    """
    project_root = get_project_root()
    logger.debug(f"Project root identified as: {project_root}")
    
    # Ensure template_dir is absolute
    template_dir = template_dir if template_dir.is_absolute() else project_root / template_dir
    logger.debug(f"Using template directory: {template_dir}")
    
    # Verify template directory structure
    if not template_dir.exists():
        raise ValueError(f"Template directory not found: {template_dir}")
    
    base_template = template_dir / 'base.md.j2'
    sections_dir = template_dir / 'sections'
    
    logger.debug(f"Looking for base template at: {base_template}")
    logger.debug(f"Looking for sections directory at: {sections_dir}")
    
    if not sections_dir.exists():
        raise ValueError(f"Sections directory not found: {sections_dir}")
    
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
    
    # Collect and order templates
    ordered_templates = collect_section_templates(sections_dir, order_config)
    logger.info(f"Found {len(ordered_templates)} templates in order: {ordered_templates}")
    
    # Set up Jinja environment
    logger.info("Setting up Jinja2 environment")
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    # Add ordered templates to variables
    variables['templates'] = ordered_templates
    
    try:
        if base_template.exists():
            logger.info(f"Found base template, attempting to render")
            template = env.get_template('base.md.j2')
            output = template.render(**variables)
            logger.info("Successfully rendered base template")
        else:
            logger.warning(f"No base template found at {base_template}, falling back to section concatenation")
            raise TemplateNotFound('base.md.j2')
            
    except Exception as e:
        logger.warning(f"Could not use base template ({str(e)}), concatenating sections instead")
        logger.info(f"Processing {len(ordered_templates)} section templates")
        
        sections = []
        for template_name in ordered_templates:
            try:
                template = env.get_template(f"sections/{template_name}")
                sections.append(template.render(**variables))
            except Exception as template_error:
                logger.error(f"Error rendering template {template_name}: {template_error}")
        
        output = '\n\n'.join(sections)
    
    logger.debug(f"Writing output to: {output_path}")
    output_path.write_text(output)
    
    if commit:
        logger.info("Committing changes")
        commit_and_push(output_path)
