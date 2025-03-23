# src/llamero/summary/concatenative.py
"""Core summary generation functionality with pathspec-based pattern matching."""
from pathlib import Path
from typing import List, Set
from loguru import logger
import pathspec
from ..config import load_config, get_pattern_spec, should_include_path

class SummaryGenerator:
    """Generate summary files for each directory in the project."""
    
    def __init__(self, root_dir: str | Path):
        """Initialize generator with root directory."""
        self.root_dir = Path(root_dir).resolve()
        self.workflow_mapping = {}  # Track workflow directory mappings
        self._load_config()
        
    def _load_config(self) -> None:
        """Load configuration from llamero config."""
        try:
            # Load from YAML config
            config = load_config()
            self.config = config.get("summary", {})
                
            # Set max file size
            self.max_file_size = self.config.get("max_file_size_kb", 1000) * 1024
            
            # Create pattern spec from exclude patterns
            exclude_patterns = self.config.get("exclude_patterns", [".git/"])
            self.pattern_spec = get_pattern_spec(exclude_patterns)
            
        except Exception as e:
            logger.warning(f"Error loading config: {e}, using minimal defaults")
            # Minimal defaults (just excluding .git)
            self.pattern_spec = get_pattern_spec([".git/"])
            self.max_file_size = 1000 * 1024  # 1000 KB default

    def _map_directory(self, directory: Path) -> Path:
        """Map directory for consistent handling of special paths like .github/workflows."""
        # Ensure we have a Path object
        directory = Path(directory)
        
        # If it's already absolute and under root_dir, make it relative first
        if directory.is_absolute():
            try:
                directory = directory.relative_to(self.root_dir)
            except ValueError:
                pass
        
        parts = list(directory.parts)
        
        # Handle .github/workflows mapping
        for i, part in enumerate(parts[:-1]):  # Don't check last part if it's a file
            if part == '.github' and i + 1 < len(parts) and parts[i + 1] == 'workflows':
                parts[i] = 'github'
                # If the original path was absolute, make result absolute
                if directory.is_absolute():
                    return self.root_dir / Path(*parts)
                return Path(*parts)
        
        # Return original path if no mapping needed
        return directory
    
    def _map_path_components(self, path: Path) -> Path:
        """Map path components according to rules."""
        mapped = self._map_directory(path)
        
        # If the mapped path is relative and we're generating files, make it absolute
        if not mapped.is_absolute() and self.root_dir:
            return self.root_dir / mapped
        
        return mapped
    
    def should_include_file(self, file_path: Path) -> bool:
        """Determine if a file should be included in the summary."""
        try:
            # Handle non-existent files
            if not file_path.exists():
                return False
                
            # Check if path should be included based on pathspec
            if not should_include_path(file_path, self.pattern_spec, self.root_dir):
                return False
                
            # Check size if threshold is set
            if self.max_file_size is not None:
                try:
                    if file_path.stat().st_size > self.max_file_size:
                        logger.debug(f"Excluding large file: {file_path} ({file_path.stat().st_size} bytes)")
                        return False
                except OSError as e:
                    logger.error(f"Error checking size of {file_path}: {e}")
                    return False
                    
            # Check if it's a binary file (simple heuristic)
            try:
                with open(file_path, 'rb') as f:
                    chunk = f.read(1024)
                    if b'\0' in chunk:  # If null bytes found, likely binary
                        logger.debug(f"Excluding likely binary file: {file_path}")
                        return False
            except Exception as e:
                logger.debug(f"Error checking if binary: {file_path}: {e}")
                
            # Default to inclusion
            return True
            
        except ValueError:
            return False
    
    def should_include_directory(self, directory: Path) -> bool:
        """Determine if a directory should have a summary generated."""
        try:
            # Special handling for workflow directories
            if '.github/workflows' in str(directory):
                return True
                
            # Check if directory should be included based on pathspec
            return should_include_path(directory, self.pattern_spec, self.root_dir)
            
        except ValueError:
            # Include root directory
            return directory.resolve() == self.root_dir
    
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
                    content = file_path.read_text(encoding='utf-8', errors='replace')
                    
                    summary.extend([
                        '---',
                        f'File: {rel_path}',
                        '---',
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
                
                # Map the directory path
                mapped_dir = self._map_path_components(directory)
                if mapped_dir:
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
                    
                    # Special case for .github/workflows
                    if '.github/workflows' in str(file_path):
                        workflows_dir = file_path.parent
                        if workflows_dir.name == 'workflows' and workflows_dir.parent.name == '.github':
                            directories.add(workflows_dir)
                            
        except Exception as e:
            logger.error(f"Error collecting directories: {e}")
        return directories
