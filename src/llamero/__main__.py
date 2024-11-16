from fire import Fire
from loguru import logger
from pathlib import Path

from .summary.concatenative import SummaryGenerator
#from .summary.python_signatures import generate_python_summary
from .summary.python_files import PythonSummariesGenerator


class Summarize:
    def __init__(self, root: str | Path ='.'):
        self.root = root
        self._concatenative = SummaryGenerator(self.root)
        self._python = PythonSummariesGenerator(self.root)
    def all(self):
        generated_files = self._concatenative.generate_all_summaries()
        return generated_files
    def python(self):
        generated_files = self._python.generate_summaries()
        return generated_files


def cli():
    fire.Fire(Summarize)


if __name__ == "__main__":
    cli()
