# src/llamero/summary/concatenative.py
"""Core summary generation functionality."""
from pathlib import Path
from typing import List, Set
from loguru import logger
from ..utils import load_config, get_project_root

class SummaryGenerator:
    """Generate summary files for each directory in the project."""
    
    DEFAULT_CONFIG = {
        "exclude_patterns": [
            '.git', '.gitignore', '.pytest_cache', '__pycache__',
            'SUMMARY', '.coverage', '.env', '.venv', '.idea', '.vscode'
        ],
        "include_extensions": [
            '.py', '.md', '.txt', '.yml', '.yaml', '.toml', 
            '.json', '.html', '.css', '.js', '.j2', '.custom'
        ],
        "exclude_directories": [
            '.git', '__pycache__', '.pytest_cache',
            '.venv', '.idea', '.vscode'
        ],
        "max_file_size_kb": 500  # Default max file size
    }
    
    def __init__(self, root_dir: str | Path):
        """Initialize generator with root directory."""
        self.root_dir = Path(root_dir).resolve()
        self._load_user_config()
        
    def _load_user_config(self) -> None:
        """Load and merge user configuration with defaults."""
        try:
            # Get the config relative to the test project directory
            found_config = False
            current_dir = self.root_dir
            while current_dir != current_dir.parent:
                config_path = current_dir / "pyproject.toml"
                if config_path.exists():
                    found_config = True
                    parsed_config = load_config(str(config_path))
                    break
                current_dir = current_dir.parent
                
            if found_config:
                user_config = parsed_config.get("tool", {}).get("summary", {})
            else:
                logger.warning(f"No pyproject.toml found in {self.root_dir} or its parents")
                user_config = {}
                
            # Start with defaults
            self.config = self.DEFAULT_CONFIG.copy()
            
            # Update with user config
            for key, value in user_config.items():
                if key in self.config and isinstance(value, list):
                    self.config[key] = value
                else:
                    self.config[key] = value
                    
            # Set max file size
            self.max_file_size = self.config["max_file_size_kb"] * 1024 if "max_file_size_kb" in self.config else None
            
        except Exception as e:
            logger.warning(f"Error loading config: {e}, using defaults")
            self.config = self.DEFAULT_CONFIG.copy()
            self.max_file_size = self.config["max_file_size_kb"] * 1024
    
    def should_include_file(self, file_path: Path) -> bool:
        """Determine if a file should be included in the summary."""
        try:
            # Get path relative to root
            rel_path = file_path.resolve().relative_to(self.root_dir)
            path_parts = rel_path.parts
            
            # Check excluded patterns
            for pattern in self.config["exclude_patterns"]:
                if any(part == pattern or part.startswith(pattern) for part in path_parts):
                    return False
            
            # Check extension
            if file_path.suffix not in self.config["include_extensions"]:
                return False
            
            # Check size if threshold is set
            if self.max_file_size is not None:
                try:
                    if file_path.stat().st_size > self.max_file_size:
                        return False
                except OSError as e:
                    logger.error(f"Error checking size of {file_path}: {e}")
                    return False
                    
            return True
        except (ValueError, OSError) as e:
            logger.error(f"Error checking file {file_path}: {e}")
            return False
    
    def should_include_directory(self, directory: Path) -> bool:
        """Determine if a directory should have a summary generated."""
        try:
            # Get path relative to root
            rel_path = directory.resolve().relative_to(self.root_dir)
            path_parts = rel_path.parts
            
            # Check excluded directories
            return not any(
                excluded == part or part.startswith(excluded)
                for excluded in self.config["exclude_directories"]
                for part in path_parts
            )
        except ValueError:
            # Include root directory
            return directory.resolve() == self.root_dir
    
    def _map_directory(self, directory: Path) -> Path:
        """Map directory to its summary location."""
        try:
            rel_path = directory.resolve().relative_to(self.root_dir)
            parts = list(rel_path.parts)
            
            # Map .github/workflows to github/workflows
            try:
                github_index = parts.index('.github')
                if len(parts) > github_index + 1 and parts[github_index + 1] == 'workflows':
                    parts[github_index] = 'github'
            except ValueError:
                pass
                
            return self.root_dir / Path(*parts)
        except ValueError:
            return directory
    
    def generate_directory_summary(self, directory: Path) -> str:
        """Generate a summary for a single directory."""
        logger.debug(f"Generating summary for {directory}")
        summary = []
        
        try:
            # Process all files in the directory
            for file_path in sorted(directory.rglob('*')):
                if not file_path.is_file() or not self.should_include_file(file_path):
                    continue
                    
                try:
                    rel_path = file_path.relative_to(self.root_dir)
                    content = file_path.read_text(encoding='utf-8')
                    
                    summary.extend([
                        '=' * 80,
                        f'File: {rel_path}',
                        '=' * 80,
                        content,
                        '\n'
                    ])
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    
            return '\n'.join(summary)
        except Exception as e:
            logger.error(f"Error generating summary for {directory}: {e}")
            return ""
    
    def generate_all_summaries(self) -> List[Path]:
        """Generate summary files for all directories."""
        logger.info("Starting summary generation")
        summary_files = []
        
        try:
            directories = self._collect_directories()
            logger.info(f"Found {len(directories)} directories to process")
            
            for directory in sorted(directories):
                if not self.should_include_directory(directory):
                    continue
                
                mapped_dir = self._map_directory(directory)
                mapped_dir.mkdir(parents=True, exist_ok=True)
                
                summary_content = self.generate_directory_summary(directory)
                if summary_content:  # Only create summary if there's content
                    summary_path = mapped_dir / 'SUMMARY'
                    summary_path.write_text(summary_content)
                    logger.info(f"Generated summary for {directory} -> {summary_path}")
                    summary_files.append(summary_path)
                    
            return summary_files
            
        except Exception as e:
            logger.error(f"Error generating summaries: {e}")
            return []
            
    def _collect_directories(self) -> Set[Path]:
        """Collect all directories containing files to summarize."""
        directories = set()
        try:
            for file_path in self.root_dir.rglob('*'):
                if (file_path.is_file() and 
                    self.should_include_file(file_path) and
                    self.should_include_directory(file_path.parent)):
                    directories.add(file_path.parent)
        except Exception as e:
            logger.error(f"Error collecting directories: {e}")
        return directories
