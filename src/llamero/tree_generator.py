from pathlib import Path
from loguru import logger
from tree_format import format_tree
from .utils import load_config
import fnmatch

def should_include_path(path: Path, ignore_patterns: set[str]) -> bool:
    """
    Determines if a path should be included based on ignore patterns.
    Matches any path component against the patterns for more granular control.
    
    Args:
        path: Path to check
        ignore_patterns: Set of glob patterns to check against
        
    Returns:
        True if path should be included, False if it matches any ignore pattern
    """
    path_parts = str(path).split('/')
    return not any(
        fnmatch.fnmatch(part, pattern)
        for pattern in ignore_patterns
        for part in path_parts
    )

def node_to_tree(path: Path, ignore_patterns: set[str]) -> tuple[str, list] | None:
    """
    Recursively converts a directory path to a tree structure.
    Filters out empty directories except for essential ones like 'docs' and 'src'.
    
    Args:
        path: Directory or file path to convert
        ignore_patterns: Set of glob patterns to filter paths
        
    Returns:
        Tuple of (node_name, child_nodes) or None if path should be excluded
    """
    if not should_include_path(path, ignore_patterns):
        return None
        
    if path.is_file():
        return path.name, []
        
    children = [
        node for child in sorted(path.iterdir())
        if (node := node_to_tree(child, ignore_patterns)) is not None
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
        ignore_patterns = set(
            config.get("tool", {})
            .get("readme", {})
            .get("tree", {})
            .get("ignore_patterns", [])
        )
    except (FileNotFoundError, KeyError):
        ignore_patterns = set()
        logger.warning("Config file or sections missing, proceeding with no ignore patterns")
    
    root_path = Path(root_dir)
    tree_root = node_to_tree(root_path, ignore_patterns)
    
    if tree_root is None:
        return ""
        
    return format_tree(
        tree_root,
        format_node=lambda x: x[0],
        get_children=lambda x: x[1]
    )
