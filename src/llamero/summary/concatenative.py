# src/llamero/summary/concatenative.py
"""Core summary generation functionality."""
from pathlib import Path
from typing import List, Set
from loguru import logger
from ..utils import load_config

class SummaryGenerator:
    """Generate summary files for each directory in the project."""
    
    def __init__(self, root_dir: str | Path):
        """Initialize generator with root directory.
        
        Args:
            root_dir: Root directory to generate summaries for
        """
        self.root_dir = Path(root_dir)
        self.max_file_size = self._load_size_threshold()
        
    def _load_size_threshold(self) -> int | None:
        """Load max file size threshold from config.
        
        Returns:
            Size threshold in bytes, or None if no threshold set
        """
        #try:
        config = load_config("pyproject.toml")
        kb_limit = config.get("tool", {}).get("summary", {}).get("max_file_size_kb")
        return kb_limit * 1024 if kb_limit is not None else None
        #except FileNotFoundError:
        #    return None

    def _collect_directories(self) -> Set[Path]:
        """Collect all directories containing files to summarize.
        
        Returns:
            Set of directory paths
        """
        directories = set()
        for file_path in self.root_dir.rglob('*'):
            if (file_path.is_file() and 
                self.should_include_file(file_path) and
                self.should_include_directory(file_path.parent)):
                directories.add(file_path.parent)
        return directories
    
    def _map_directory(self, directory: Path) -> Path:
        """Map directory to its summary location.
        
        Maps .github/workflows to github/workflows for security compliance.
        
        Args:
            directory: Original directory path
        
        Returns:
            Mapped directory path
        """
        # Convert .github/workflows to github/workflows
        if '.github/workflows' in str(directory):
            parts = list(directory.parts)
            github_index = parts.index('.github')
            parts[github_index] = 'github'
            return Path(*parts)
        return directory

    def _map_path(self, path: Path) -> Path:
        """Map file path to its summary location.
        
        Args:
            path: Original file path
        
        Returns:
            Mapped file path
        """
        return self._map_directory(path.parent) / path.name

    def should_include_file(self, file_path: Path) -> bool:
        """Determine if a file should be included in the summary.
        
        Args:
            file_path: Path to file to check
            
        Returns:
            True if file should be included in summary
        """
        # Skip common files we don't want to summarize
        excluded_files = {
            '.git', '.gitignore', '.pytest_cache', '__pycache__',
            'SUMMARY', '.coverage', '.env', '.venv', '.idea', '.vscode'
        }
        
        # Skip excluded directories and files
        if any(part in excluded_files for part in file_path.parts):
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
            
        # Only include text files
        text_extensions = {'.py', '.md', '.txt', '.yml', '.yaml', '.toml', 
                         '.json', '.html', '.css', '.js', '.j2'}
        return file_path.suffix in text_extensions
    
    def should_include_directory(self, directory: Path) -> bool:
        """Determine if a directory should have a summary generated.
        
        Args:
            directory: Directory to check
            
        Returns:
            True if directory should have a summary
        """
        # Skip other excluded directories
        excluded_dirs = {
            '.git', '__pycache__', '.pytest_cache',
            '.venv', '.idea', '.vscode'
        }
        
        return not any(part in excluded_dirs for part in directory.parts)
    
    def generate_directory_summary(self, directory: Path) -> str:
        """Generate a summary for a single directory.
        
        Args:
            directory: Directory to generate summary for
            
        Returns:
            Generated summary text
        """
        logger.debug(f"Generating summary for {directory}")
        summary = []
        
        # Process all files in the directory
        for file_path in sorted(directory.rglob('*')):
            if not file_path.is_file() or not self.should_include_file(file_path):
                continue
                
            try:
                # Get relative path from root for the header
                rel_path = file_path.relative_to(self.root_dir)
                
                # Read file content
                content = file_path.read_text(encoding='utf-8')
                
                # Add to summary with clear separation
                summary.extend([
                    '=' * 80,
                    f'File: {rel_path}',  # Original path in header for reference
                    '=' * 80,
                    content,
                    '\n'  # Extra newline for separation
                ])
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                
        return '\n'.join(summary)
        
    def generate_all_summaries(self) -> List[Path]:
        """Generate summary files for all directories.
        
        Returns:
            List of paths to generated summary files
        """
        logger.info("Starting summary generation")
        summary_files = []
        
        # Collect directories
        directories = self._collect_directories()
        logger.info(f"Found {len(directories)} directories to process")
        
        # Generate summaries
        for directory in sorted(directories):
            if not self.should_include_directory(directory):
                continue
            
            # Map directory for summary placement
            summary_dir = self._map_directory(directory)
            summary_dir.mkdir(parents=True, exist_ok=True)
            
            summary_content = self.generate_directory_summary(directory)
            summary_path = summary_dir / 'SUMMARY'
            
            try:
                summary_path.write_text(summary_content, encoding='utf-8')
                logger.info(f"Generated summary for {directory} -> {summary_path}")
                summary_files.append(summary_path)
            except Exception as e:
                logger.error(f"Error writing summary for {directory}: {e}")
                
        return summary_files
