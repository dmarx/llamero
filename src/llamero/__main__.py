import fire
from loguru import logger
from pathlib import Path

from .summary.concatenative import SummaryGenerator
from .summary.python_files import PythonSummariesGenerator
from .tree_generator import generate_tree
from .utils import commit_and_push, commit_and_push_to_branch, get_project_root


class tree:
    """Commands for generating and managing project tree structure"""
    
    def generate(self, output: str | None = None, commit: bool = True) -> None:
        """
        Generate a tree representation of the project structure
        
        Args:
            output: Optional output path. Defaults to docs/readme/sections/structure.md.j2
            commit: Whether to commit changes to git. Defaults to True
        """
        tree_content = generate_tree(".")
        
        if not tree_content:
            logger.warning("No tree structure generated - check ignore patterns in config")
            return
            
        if output is None:
            # Default to readme section template
            output = "docs/readme/sections/structure.md.j2"
        
        output_path = Path(output)
        if not output_path.is_absolute():
            output_path = get_project_root() / output_path
            
        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
            
        # Format as markdown with header and code block
        content = [
            "## Project Structure",
            "",
            "```",
            tree_content,
            "```",
            ""
        ]
        
        output_path.write_text("\n".join(content))
        logger.info(f"Tree structure written to {output_path}")
        
        if commit:
            commit_and_push(output_path)


class summarize:
    def __init__(self, root: str | Path ='.'):
        self.root = root
        self._concatenative = SummaryGenerator(self.root)
        self._python = PythonSummariesGenerator(self.root)

    def _finish(self, files: list[str|Path] ):
        commit_and_push_to_branch(
            message="Update directory summaries and special summaries",
            branch="summaries",
            paths=files,
            force=True
        )

    def main(self):
        """Generates concatenative summaries"""
        generated_files = self._concatenative.generate_all_summaries()
        self._finish(generated_files)

    def python(self):
        """Generates summaries for python code"""
        generated_files = self._python.generate_summaries()
        self._finish(generated_files)

    def all(self):
        """Generates all supported summaries"""
        self.main()
        self.python()


def cli():
    fire.Fire()

if __name__ == "__main__":
    cli()
