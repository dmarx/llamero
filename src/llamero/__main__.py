import fire
from loguru import logger
from pathlib import Path

from .summary.concatenative import SummaryGenerator
from .summary.python_files import PythonSummariesGenerator
from .tree_generator import generate_tree
from .dir2doc import compile_template_dir
from .utils import commit_and_push, commit_and_push_to_branch, get_project_root, load_config


def build_template(
    template_dir: str | Path, 
    output_path: str | Path | None = None,
    variables: dict | None = None,
    commit: bool = True
) -> None:
    """
    Build a document from a template directory
    
    Args:
        template_dir: Path to template directory
        output_path: Optional explicit output path. If None, uses directory name
        variables: Optional variables to pass to template rendering
        commit: Whether to commit changes to git
    """
    template_path = Path(template_dir)
    if not template_path.is_absolute():
        template_path = get_project_root() / template_path
        
    try:
        config = load_config("pyproject.toml")
        # Get section order from config if this is a readme template
        if template_path.name == "readme":
            order_config = config.get("tool", {}).get("readme", {}).get("sections", {}).get("order", {})
        else:
            order_config = None
    except FileNotFoundError:
        logger.warning("No pyproject.toml found, proceeding without section ordering")
        order_config = None
        
    if output_path:
        output_path = Path(output_path)
        if not output_path.is_absolute():
            output_path = get_project_root() / output_path
            
    compile_template_dir(
        template_dir=template_path,
        output_path=output_path,
        variables=variables,
        order_config=order_config,
        commit=commit
    )


def tree(output: str | None = None, commit: bool = True) -> None:
    """
    Generate a tree representation of the project structure
    
    Args:
        output: Optional output path. Defaults to docs/readme/sections/structure.md.j2
        commit: Whether to commit changes to git
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
    output_path.parent.mkdir(parents=True, exist_ok=True)
        
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

def readme(commit: bool = True) -> None:
    """
    Generate the project README
    
    This is a convenience command that:
    1. Generates the project tree
    2. Builds the README from templates
    
    Args:
        commit: Whether to commit changes to git
    """
    logger.info("Generating project tree...")
    # TODO: if these functions return the names of files modified/created, we can 
    # pass them to commit_and_push once instead of committing multiple times per
    # update
    tree(commit=commit)
    
    logger.info("Building README from templates...")
    template_dir = get_project_root() / 'docs/readme'
    build_template(template_dir=template_dir, commit=commit)
    
    logger.info("README generation complete")


class Summarize:
    """Generate project summaries"""
    
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
    fire.Fire({
        'build_template': build_template,
        'tree': tree,
        'readme': readme,
        'summarize': Summarize
    })

if __name__ == "__main__":
    cli()
