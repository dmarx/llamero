# src/llamero/config.py (using pathspec library)
"""Configuration loading and management for Llamero."""
from pathlib import Path
import yaml
from loguru import logger
import os
import pathspec  # Standard library for gitignore-style pattern matching

# Default configuration with minimal exclusions
DEFAULT_CONFIG = {
    "summary": {
        # Maximum file size in KB to include (prevents massive files from being processed)
        "max_file_size_kb": 1000
    },
    "tree": {
        # Empty by default - patterns loaded from .llameroignore
    },
    "readme": {
        "sections_order": {}  # Empty by default
    }
}

def read_ignore_file() -> list[str]:
    """
    Read .llameroignore file if it exists, or use .gitignore patterns.
    Returns a list of patterns to ignore.
    """
    ignore_patterns = []
    
    # First check for .llameroignore
    ignore_file = Path.cwd() / ".llameroignore"
    if ignore_file.exists():
        try:
            with open(ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        ignore_patterns.append(line)
            logger.debug(f"Loaded {len(ignore_patterns)} patterns from .llameroignore")
        except Exception as e:
            logger.warning(f"Error reading .llameroignore: {e}")
    
    # If no .llameroignore, check for .gitignore
    elif (Path.cwd() / ".gitignore").exists():
        try:
            with open(Path.cwd() / ".gitignore", 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        ignore_patterns.append(line)
            logger.debug(f"Loaded {len(ignore_patterns)} patterns from .gitignore")
        except Exception as e:
            logger.warning(f"Error reading .gitignore: {e}")
    
    # If no ignore files found, use minimal defaults
    if not ignore_patterns:
        ignore_patterns = [".git/"]
        logger.debug("No ignore file found, using minimal defaults (.git/)")
    
    return ignore_patterns

def load_config() -> dict:
    """
    Load Llamero configuration, merging with defaults and ignore patterns.
    """
    # Start with defaults
    config = DEFAULT_CONFIG.copy()
    
    # Load user config if exists
    config_path = Path.cwd() / ".llamero.yml"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                
            if user_config:
                # Merge configs
                for section, values in user_config.items():
                    if section in config:
                        config[section].update(values)
                    else:
                        config[section] = values
                        
            logger.debug(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.warning(f"Error loading config from {config_path}: {e}")
    else:
        logger.debug("No .llamero.yml found, using defaults")
    
    # Add patterns from .llameroignore or .gitignore
    ignore_patterns = read_ignore_file()
    if ignore_patterns:
        # Store patterns for both summary and tree
        if "exclude_patterns" not in config["summary"]:
            config["summary"]["exclude_patterns"] = ignore_patterns
        if "exclude_patterns" not in config["tree"]:
            config["tree"]["exclude_patterns"] = ignore_patterns
    
    return config

def create_llameroignore() -> Path:
    """
    Create a default .llameroignore file with common exclusions.
    Returns the path to the created file.
    """
    ignore_path = Path.cwd() / ".llameroignore"
    
    with open(ignore_path, 'w') as f:
        f.write("""# Llamero ignore file
# Lines starting with # are comments
# This file uses .gitignore-style pattern matching:
#   * - matches any sequence of characters except /
#   ? - matches any single character except /
#   ** - matches any sequence of characters including /
#   / at the end of pattern - pattern matches directories only
#   ! at the beginning of pattern - negates the pattern (include instead of exclude)

# Version control
.git/
.gitignore
.gitmodules
.gitattributes

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/

# Virtual environments
.env
.venv
env/
venv/
ENV/

# IDE files
.idea/
.vscode/
*.swp
*.swo
*~

# Logs and databases
*.log
*.sqlite
*.db

# OS specific
.DS_Store
Thumbs.db

# Examples of more advanced patterns:
# **/node_modules/    # Ignore node_modules anywhere in the repository
# docs/**/temp/       # Ignore temp directories under docs, at any level
# **/data/**/*.csv    # Ignore all CSV files in any data directory

# Override examples (uncomment to use):
# !.git/config        # Include git config despite ignoring .git/
# !**/*.md            # Include all markdown files even if they'd be ignored
# !important.log      # Include this specific log file
""")
    
    logger.info(f"Created default .llameroignore at {ignore_path}")
    return ignore_path

def create_default_config() -> Path:
    """
    Create a default configuration file.
    Returns the path to the created file.
    """
    config_path = Path.cwd() / ".llamero.yml"
    
    with open(config_path, 'w') as f:
        f.write("""# Llamero Configuration

# Summary generation settings
summary:
  # Maximum file size in KB to include
  max_file_size_kb: 1000
  
  # Additional exclude patterns beyond .llameroignore
  # (generally you should use .llameroignore instead)
  # exclude_patterns:
  #   - "some_specific_file.txt"

# Tree generation settings
tree:
  # Additional exclude patterns for tree generation
  # exclude_patterns:
  #   - "node_modules/"

# README generation settings
readme:
  # Configure section ordering for README generation
  sections_order: {}
  # Example ordering:
  # sections_order:
  #   introduction.md.j2: 1
  #   features.md.j2: 2
  #   usage.md.j2: 3
""")
    
    logger.info(f"Created default configuration at {config_path}")
    return config_path

def get_pattern_spec(exclude_patterns):
    """Create a pathspec object from gitignore-style patterns."""
    try:
        return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, exclude_patterns)
    except Exception as e:
        logger.error(f"Error creating pattern spec: {e}")
        # Return a spec that only matches .git as a fallback
        return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, [".git/"])

def should_include_path(path: Path, pattern_spec, root_dir: Path = None) -> bool:
    """
    Determine if a path should be included based on the pathspec.
    
    Args:
        path: Path to check
        pattern_spec: PathSpec object or list of patterns
        root_dir: Optional root directory for relative paths
        
    Returns:
        True if path should be included, False if it should be excluded
    """
    # If we got a list of patterns, convert to PathSpec
    if isinstance(pattern_spec, list):
        pattern_spec = get_pattern_spec(pattern_spec)
        
    # Convert to relative path if root_dir is provided
    if root_dir:
        try:
            rel_path = path.relative_to(root_dir)
            path_str = str(rel_path)
        except ValueError:
            path_str = str(path)
    else:
        path_str = str(path)
        
    # pathspec.match_file returns True if path should be EXCLUDED
    # We want the opposite (True if path should be INCLUDED)
    return not pattern_spec.match_file(path_str)
