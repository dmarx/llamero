"""Special summary generators for project-wide summaries."""
from pathlib import Path
from loguru import logger
from .python_signatures import SignatureExtractor, generate_python_summary


class PythonSummariesGenerator:
    """Generate special project-wide summary files."""
    
    def __init__(self, root_dir: str | Path):
        """Initialize generator with root directory."""
        self.root_dir = Path(root_dir)
        self.summaries_dir = self.root_dir / "SUMMARIES"
        self.signature_extractor = SignatureExtractor()  # New instance

    def generate_summaries(self) -> list[Path]:
        """Generate all special summary files.
        
        Returns:
            List of paths to generated summary files
        """
        self.summaries_dir.mkdir(exist_ok=True)
        generated_files = []

        python_path = self.summaries_dir / "PYTHON.md"
        python_content = generate_python_summary(self.root_dir)  # Using new generator
        python_path.write_text(python_content)
        generated_files.append(python_path)
        
        return generated_files


if __name__ == "__main__":
    summarizer = PythonSummariesGenerator(".")
    summarizer.generate_summaries()
