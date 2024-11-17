from pathlib import Path
from loguru import logger
from tree_format import format_tree
from .utils import load_config


def should_include_path(path: Path, config: dict) -> bool:
    """
    Determines if a path should be included based on config ignore patterns.
    Matches path components exactly against ignore patterns.
    
    Args:
        path: Path to check
        config: Config dict containing ignore patterns under tool.readme.tree.ignore_patterns
        
    Returns:
        True if path should be included, False if it matches any ignore pattern
    """
    ignore_patterns = config.get("tool", {}).get("readme", {}).get("tree", {}).get("ignore_patterns", [])
    
    # Convert path to parts for matching
    parts = path.parts
    if not parts:  # Handle empty path
        return True
        
    for pattern in ignore_patterns:
        # Handle file extension patterns (e.g. *.pyc)
        if pattern.startswith('*'):
            if str(path).endswith(pattern[1:]):
                return False
        # Handle directory/file name patterns
        elif pattern in parts or (pattern == str(path.name)):
            return False
    return True

def node_to_tree(path: Path, config: dict) -> tuple[str, list] | None:
    """
    Recursively converts a directory path to a tree structure.
    Filters out empty directories except for essential ones like 'docs' and 'src'.
    
    Args:
        path: Directory or file path to convert
        config: Config dict containing ignore patterns
        
    Returns:
        Tuple of (node_name, child_nodes) or None if path should be excluded
    """
    if not should_include_path(path, config):
        return None
        
    if path.is_file():
        return path.name, []
        
    children = [
        node for child in sorted(path.iterdir())
        if (node := node_to_tree(child, config)) is not None
    ]
    
    if not children and path.name not in {'docs', 'src'}:
        return None
        
    return path.name, children

def generate_tree(root_dir: str = ".") -> str:
    """
    Generates a formatted directory tree string starting from root_dir.
    Handles missing config files and sections gracefully.
    
    Args:
        root_dir: Root directory to start tree generation from
        
    Returns:
        Formatted string representation of the directory tree
    """
    try:
        config = load_config("pyproject.toml")
    except (FileNotFoundError, KeyError):
        config = {"tool": {"readme": {"tree": {"ignore_patterns": []}}}}
        logger.warning("Config file or sections missing, proceeding with no ignore patterns")
    
    root_path = Path(root_dir)
    tree_root = node_to_tree(root_path, config)
    
    if tree_root is None:
        return ""
        
    return format_tree(
        tree_root,
        format_node=lambda x: x[0],
        get_children=lambda x: x[1]
    )
