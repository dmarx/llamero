"""Special summary generators for project-wide summaries."""
from pathlib import Path
from typing import List
from loguru import logger


class ReadmeSummariesGenerator:
    """Generate special project-wide summary files."""
    
    def __init__(self, root_dir: str | Path):
        """Initialize generator with root directory."""
        self.root_dir = Path(root_dir)
        self.summaries_dir = self.root_dir / "SUMMARIES"
    
    def _find_readmes(self, include_root: bool = True) -> List[Path]:
        """Find all README files in the project."""
        readmes = []
        for file in self.root_dir.rglob("README.md"):
            if not include_root and file.parent == self.root_dir:
                continue
            readmes.append(file)
        return sorted(readmes)
    
    def generate_readme_summaries(self) -> List[Path]:
        """Generate all special summary files.
        
        Returns:
            List of paths to generated summary files
        """
        self.summaries_dir.mkdir(exist_ok=True)
        generated_files = []
        
        # Generate READMEs.md
        readmes_path = self.summaries_dir / "READMEs.md"
        readme_content = []
        for readme in self._find_readmes(include_root=True):
            rel_path = readme.relative_to(self.root_dir)
            readme_content.extend([
                "=" * 80,
                f"# {rel_path}",
                "=" * 80,
                readme.read_text(),
                "\n"
            ])
        readmes_path.write_text("\n".join(readme_content))
        generated_files.append(readmes_path)
        
        # Generate README_SUBs.md
        subs_path = self.summaries_dir / "README_SUBs.md"
        subs_content = []
        for readme in self._find_readmes(include_root=False):
            rel_path = readme.relative_to(self.root_dir)
            subs_content.extend([
                "=" * 80,
                f"# {rel_path}",
                "=" * 80,
                readme.read_text(),
                "\n"
            ])
        subs_path.write_text("\n".join(subs_content))
        generated_files.append(subs_path)
                
        return generated_files

if __name__ == "__main__":
    summarizer = ReadmeSummariesGenerator('.')
    summarizer.generate_readme_summaries()
