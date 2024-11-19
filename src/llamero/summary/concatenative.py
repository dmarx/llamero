# src/llamero/summary/concatenative.py
"""Core summary generation functionality."""
from pathlib import Path
from typing import List, Set
from loguru import logger
from ..utils import load_config

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
        ]
    }
    
    def __init__(self, root_dir: str | Path):
        """Initialize generator with root directory.
        
        Args:
            root_dir: Root directory to generate summaries for
        """
        self.root_dir = Path(root_dir)
        self.config = self._load_config()
        self.max_file_size = self._load_size_threshold()
        
    def _load_config(self) -> dict:
        """Load summary configuration from pyproject.toml.
        
        Returns:
            Dictionary containing summary configuration
        """
        try:
            parsed_config = load_config("pyproject.toml")
            user_config = parsed_config.get("tool", {}).get("summary", {})
            
            # Deep copy default config
            result = {
                key: list(value) if isinstance(value, list) else value
                for key, value in self.DEFAULT_CONFIG.items()
            }
            
            # Merge with user config
            for key, value in user_config.items():
                if key in result and isinstance(value, list):
                    result[key] = value
                elif key not in ['max_file_size_kb']:
                    result[key] = value
                    
            return result
            
        except FileNotFoundError:
            logger.warning("No pyproject.toml found, using default configuration")
            return self.DEFAULT_CONFIG.copy()
            
    def _load_size_threshold(self) -> int | None:
        """Load max file size threshold from config.
        
        Returns:
            Size threshold in bytes, or None if no threshold set
        """
        try:
            config = load_config("pyproject.toml")
            kb_limit = config.get("tool", {}).get("summary", {}).get("max_file_size_kb")
            return kb_limit * 1024 if kb_limit is not None else None
        except FileNotFoundError:
            return None

    def _collect_directories(self) -> Set[Path]:
        """Collect all directories containing files to summarize."""
        directories = set()
        for file_path in self.root_dir.rglob('*'):
            if (file_path.is_file() and 
                self.should_include_file(file_path) and
                self.should_include_directory(file_path.parent)):
                directories.add(file_path.parent)
        return directories
    
    def _map_directory(self, directory: Path) -> Path:
        """Map directory to its summary location."""
        # Convert .github/workflows to github/workflows
        parts = list(directory.parts)
        try:
            github_index = parts.index('.github')
            if len(parts) > github_index + 1 and parts[github_index + 1] == 'workflows':
                parts[github_index] = 'github'
                return Path(*parts)
        except ValueError:
            pass
        return directory

    def should_include_file(self, file_path: Path) -> bool:
        """Determine if a file should be included in the summary."""
        try:
            # Skip excluded patterns
            path_str = str(file_path.relative_to(self.root_dir))
            for pattern in self.config["exclude_patterns"]:
                if pattern in path_str.split('/'):
                    return False
                
            # Check file size if threshold is set
            if self.max_file_size is not None:
                try:
                    file_size = file_path.stat().st_size
                    if file_size > self.max_file_size:
                        logger.warning(
                            f"Skipping large file {file_path} ({file_size/1024:.1f}KB > {self.max_file_size/1024:.1f}KB threshold)"
                        )
                        return False
                except OSError as e:
                    logger.error(f"Error checking size of {file_path}: {e}")
                    return False
                
            # Check file extension
            return file_path.suffix in self.config["include_extensions"]
            
        except ValueError:
            return False
    
    def should_include_directory(self, directory: Path) -> bool:
        """Determine if a directory should have a summary generated."""
        try:
            path_str = str(directory.relative_to(self.root_dir))
            return not any(excluded in path_str.split('/') for excluded in self.config["exclude_directories"])
        except ValueError:
            return True  # Include root directory
    
    def generate_directory_summary(self, directory: Path) -> str:
        """Generate a summary for a single directory."""
        logger.debug(f"Generating summary for {directory}")
        summary = []
        
        # Process all files in the directory
        for file_path in sorted(directory.rglob('*')):
            if not file_path.is_file() or not self.should_include_file(file_path):
                continue
                
            try:
                # Get relative path from root for the header
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
        
    def generate_all_summaries(self) -> List[Path]:
        """Generate summary files for all directories."""
        logger.info("Starting summary generation")
        summary_files = []
        directories = self._collect_directories()
        logger.info(f"Found {len(directories)} directories to process")
        
        for directory in sorted(directories):
            if not self.should_include_directory(directory):
                continue
            
            summary_dir = self._map_directory(directory)
            summary_dir.mkdir(parents=True, exist_ok=True)
            
            summary_content = self.generate_directory_summary(directory)
            summary_path = summary_dir / 'SUMMARY'
            
            try:
                summary_path.write_text(summary_content, encoding='utf-8')
                logger.info(f"Generated summary for {directory} -> {summary_path}")
                summary_files.append(self._map_directory(summary_path))
            except Exception as e:
                logger.error(f"Error writing summary for {directory}: {e}")
                continue
                
        return summary_files
