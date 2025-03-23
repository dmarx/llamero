# src/llamero/tree_generator.py
from pathlib import Path
from loguru import logger
from tree_format import format_tree
from .config import load_config, get_pattern_spec, should_include_path

def node_to_tree(path: Path, pattern_spec, root_dir: Path) -> tuple[str, list] | None:
    """
    Recursively converts a directory path to a tree structure.
    Filters out excluded paths and empty directories (except for essential ones).
    
    Args:
        path: Directory or file path to convert
        pattern_spec: pathspec.PathSpec object for pattern matching
        root_dir: Root directory for relative path calculation
        
    Returns:
        Tuple of (node_name, child_nodes) or None if path should be excluded
    """
    # Check if path should be included
    if not should_include_path(path, pattern_spec, root_dir):
        return None
        
    # Handle files
    if path.is_file():
        return path.name, []
        
    # Process directory children
    children = [
        node for child in sorted(path.iterdir())
        if (node := node_to_tree(child, pattern_spec, root_dir)) is not None
    ]
    
    # Keep essential directories even if empty
    if not children and path.name not in {'docs', 'src', 'tests'}:
        return None
        
    return path.name, children

def generate_tree(root_dir: str = ".") -> str:
    """
    Generates a formatted directory tree string starting from root_dir.
    Uses pathspec for gitignore-style pattern matching.
    
    Args:
        root_dir: Root directory to start tree generation from
        
    Returns:
        Formatted string representation of the directory tree
    """
    root_path = Path(root_dir).resolve()
    
    try:
        # Use new configuration system
        config = load_config()
        exclude_patterns = config.get('tree', {}).get('exclude_patterns', [".git/"])
        pattern_spec = get_pattern_spec(exclude_patterns)
        logger.debug(f"Using {len(exclude_patterns)} exclude patterns for tree generation")
    except Exception as e:
        logger.warning(f"Error loading config: {e}, proceeding with minimal defaults")
        pattern_spec = get_pattern_spec([".git/"])
    
    tree_root = node_to_tree(root_path, pattern_spec, root_path)
    
    if tree_root is None:
        return ""
        
    return format_tree(
        tree_root,
        format_node=lambda x: x[0],
        get_children=lambda x: x[1]
    )
