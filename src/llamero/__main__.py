import fire
from loguru import logger
from pathlib import Path

from .summary.concatenative import SummaryGenerator
#from .summary.python_signatures import generate_python_summary
from .summary.python_files import PythonSummariesGenerator
from .utils import commit_and_push_to_branch

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
            #base_branch="main", # should be current branch
            force=True  # Use force push for generated content
        )
    def main(self):
        """
        Generates concatenative summaries
        """
        generated_files = self._concatenative.generate_all_summaries()
        self._finish(generated_files)
    def python(self):
        """
        Generates summaries for python code
        """
        generated_files = self._python.generate_summaries()
        self._finish(generated_files)
    def all(self):
        """
        Generates all supported summaries 
        """
        self.main()
        self.python()


def cli():
    fire.Fire()


if __name__ == "__main__":
    cli()
