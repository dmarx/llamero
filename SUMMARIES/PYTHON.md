# Python Project Structure

## src/llamero/__main__.py
```python
def build_template(template_dir: str | Path, output_path: str | Path | None, variables: dict | None, commit: bool) -> None
    """
    Build a document from a template directory
    Args:
        template_dir: Path to template directory
        output_path: Optional explicit output path. If None, uses directory name
        variables: Optional variables to pass to template rendering
        commit: Whether to commit changes to git
    """

def tree(output: str | None, commit: bool) -> None
    """
    Generate a tree representation of the project structure
    Args:
        output: Optional output path. Defaults to docs/readme/sections/structure.md.j2
        commit: Whether to commit changes to git
    """

def readme(commit: bool) -> None
    """
    Generate the project README
    This is a convenience command that:
    1. Generates the project tree
    2. Builds the README from templates
    Args:
        commit: Whether to commit changes to git
    """

class Summarize
    """Generate project summaries"""

    def __init__(self, root: str | Path)

    def _finish(self, files: list[str | Path])

    def main(self)
        """Generates concatenative summaries"""

    def python(self)
        """Generates summaries for python code"""

    def all(self)
        """Generates all supported summaries"""


def cli()

```

## src/llamero/dir2doc.py
```python
def collect_section_templates(sections_dir: Path, order_config: dict | None) -> list[str]
    """
    Collect and order section templates from a directory.
    Args:
        sections_dir: Directory containing section templates
        order_config: Optional mapping of template names to order values from config
    Returns:
        List of template names in correct order
    """

def compile_template_dir(template_dir: Path, output_path: Path | None, variables: Dict | None, order_config: Dict | None, commit: bool) -> None
    """
    Compile a directory of templates into a single output file.
    Args:
        template_dir: Path to template directory
        output_path: Optional explicit output path. If None, uses directory name
        variables: Optional variables to pass to template rendering
        order_config: Optional dictionary defining template ordering
        commit: Whether to commit and push changes
    """

```

## src/llamero/summary/concatenative.py
```python
class SummaryGenerator
    """Generate summary files for each directory in the project."""

    def __init__(self, root_dir: str | Path)
        """Initialize generator with root directory."""

    def _load_user_config(self) -> None
        """Load and merge user configuration with defaults."""

    def _map_directory(self, directory: Path) -> Path
        """Map directory for consistent handling of special paths like .github/workflows."""

    def _map_path_components(self, path: Path) -> Path
        """Map path components according to rules."""

    def should_include_file(self, file_path: Path) -> bool
        """Determine if a file should be included in the summary."""

    def should_include_directory(self, directory: Path) -> bool
        """Determine if a directory should have a summary generated."""

    def generate_directory_summary(self, directory: Path) -> str
        """Generate a summary for a single directory."""

    def _generate_aggregated_summary(self, directory: Path) -> str | None
        """
        Generate aggregated summary content from child SUMMARY files.
        Returns None if no child summaries exist.
        Args:
            directory: Directory to generate aggregated summary for
        Returns:
            Concatenated summary content or None if no summaries found
        """

    def generate_all_summaries(self) -> List[Path]
        """Generate summary files for all directories, including aggregated summaries."""

    def _collect_directories(self) -> Set[Path]
        """Collect all directories containing files to summarize."""


```

## src/llamero/summary/python_files.py
```python
class PythonSummariesGenerator
    """Generate special project-wide summary files."""

    def __init__(self, root_dir: str | Path)
        """Initialize generator with root directory."""

    def generate_summaries(self) -> list[Path]
        """
        Generate all special summary files.
        Returns:
            List of paths to generated summary files
        """


```

## src/llamero/summary/python_signatures.py
```python
@dataclass
class Signature
    """Represents a Python function or class signature with documentation."""

class ParentNodeTransformer
    """Add parent references to all nodes in the AST."""

    def visit(self, node: Any) -> Any
        """Visit a node and add parent references to all its children."""


class SignatureExtractor
    """Extracts detailed signatures from Python files."""

    def get_type_annotation(self, node: Any) -> str
        """Convert AST annotation node to string representation."""

    def get_arg_string(self, arg: Any) -> str
        """Convert function argument to string with type annotation."""

    def extract_signatures(self, source: str) -> List[Signature]
        """Extract all function and class signatures from source code."""

    def format_signature(self, sig: Signature, indent: int) -> List[str]
        """Format a signature for display with proper indentation."""


def generate_python_summary(root_dir: str | Path) -> str
    """
    Generate enhanced Python project structure summary.
    Args:
        root_dir: Root directory of the project
    Returns:
        Formatted markdown string of Python signatures
    """

```

## src/llamero/summary/readmes.py
```python
class ReadmeSummariesGenerator
    """Generate special project-wide summary files."""

    def __init__(self, root_dir: str | Path)
        """Initialize generator with root directory."""

    def _find_readmes(self, include_root: bool) -> List[Path]
        """Find all README files in the project."""

    def generate_readme_summaries(self) -> List[Path]
        """
        Generate all special summary files.
        Returns:
            List of paths to generated summary files
        """


```

## src/llamero/tree_generator.py
```python
def should_include_path(path: Path, config: dict) -> bool
    """
    Determines if a path should be included based on config ignore patterns.
    Matches path components exactly against ignore patterns.
    Args:
        path: Path to check
        config: Config dict containing ignore patterns under tool.readme.tree.ignore_patterns
    Returns:
        True if path should be included, False if it matches any ignore pattern
    """

def node_to_tree(path: Path, config: dict) -> tuple[[str, list]] | None
    """
    Recursively converts a directory path to a tree structure.
    Filters out empty directories except for essential ones like 'docs' and 'src'.
    Args:
        path: Directory or file path to convert
        config: Config dict containing ignore patterns
    Returns:
        Tuple of (node_name, child_nodes) or None if path should be excluded
    """

def generate_tree(root_dir: str) -> str
    """
    Generates a formatted directory tree string starting from root_dir.
    Handles missing config files and sections gracefully.
    Args:
        root_dir: Root directory to start tree generation from
    Returns:
        Formatted string representation of the directory tree
    """

```

## src/llamero/utils.py
```python
def get_project_root() -> Path
    """
    Get the project root directory by looking for pyproject.toml
    Returns the absolute path to the project root
    """

def load_config(config_path: str) -> dict
    """
    Load configuration from a TOML file
    Args:
        config_path (str): Path to the TOML configuration file relative to project root
    Returns:
        dict: Parsed configuration data
    """

def commit_and_push(files_to_commit: str | Path | list[str] | list[Path], message)
    """Commit and push changes for a specific file"""

def commit_and_push_to_branch(message: str, branch: str, paths: list[str | Path], base_branch: str | None, force: bool) -> None
    """
    Commit changes and push to specified branch.
    Args:
        message: Commit message
        branch: Branch to push to
        paths: List of paths to commit
        base_branch: Optional base branch to create new branch from
        force: If True, create fresh branch and force push (for generated content)
    """

```

## tests/conftest.py
```python
class InterceptHandler

    def emit(self, record)


def setup_logging(caplog)
    """Set up loguru to work with pytest's caplog."""

def temp_project_dir()
    """Create a temporary project directory with a pyproject.toml."""

def mock_git_repo(temp_project_dir)
    """Create a temporary git repository."""

```

## tests/test_dir2doc.py
```python
def test_collect_section_templates(temp_project_dir)
    """Test template collection and ordering."""

def test_compile_template_dir_with_base(temp_project_dir)
    """Test template compilation with base template."""

def test_compile_template_dir_without_base(temp_project_dir)
    """Test template compilation without base template (fallback mode)."""

def test_compile_template_dir_with_ordering(temp_project_dir)
    """Test template compilation with explicit ordering."""

```

## tests/test_summary/test_aggregation.py
```python
def create_nested_summaries(root_dir: Path) -> dict[[str, Path]]
    """Create a nested directory structure with SUMMARY files."""

def test_basic_aggregation(temp_project_dir)
    """Test basic summary aggregation in a nested directory structure."""

def test_aggregation_with_empty_directories(temp_project_dir)
    """Test that empty directories don't affect aggregation."""

def test_aggregation_content_preservation(temp_project_dir)
    """Test that all content is preserved during aggregation."""

def test_aggregation_with_excluded_directories(temp_project_dir)
    """Test that excluded directories don't affect aggregation."""

```

## tests/test_summary/test_concatenative.py
```python
def config_project_dir(temp_project_dir)
    """Create a project directory with custom configuration."""

def workflow_project_dir(temp_project_dir)
    """Create a project directory with workflow files."""

def test_files(config_project_dir)
    """Create a set of test files with various extensions and patterns."""

def test_config_loading(config_project_dir)
    """Test that configuration is properly loaded from pyproject.toml."""

def test_file_inclusion_by_extension(test_files)
    """Test that files are correctly included/excluded based on extension."""

def test_file_exclusion_by_pattern(test_files)
    """Test that files are correctly excluded based on patterns."""

def test_directory_exclusion(test_files)
    """Test that directories are correctly excluded."""

def test_file_size_limits(test_files)
    """Test that files are excluded based on size limits."""

def test_nested_directory_handling(test_files)
    """Test that nested directories are handled correctly."""

def test_default_config_fallback(temp_project_dir)
    """Test that default configuration is used when no config file exists."""

def test_workflow_directory_mapping(workflow_project_dir)
    """Test that .github/workflows is correctly mapped to github/workflows."""

def test_error_handling(config_project_dir, caplog)
    """Test error handling for unreadable files."""

def test_excluded_directory_files(test_files)
    """Test that files in excluded directories are excluded regardless of extension."""

```

## tests/test_summary/test_python_signatures.py
```python
def test_signature_extraction()
    """Test Python signature extraction."""

def test_generate_python_summary(temp_project_dir)
    """Test Python summary generation."""

```

## tests/test_summary/test_size_limits.py
```python
def test_file_size_threshold_config(temp_project_dir, monkeypatch)
    """Test that size threshold is properly loaded from config."""

def test_file_size_filtering(temp_project_dir, monkeypatch)
    """Test that files are filtered based on size."""

def test_directory_summary_with_size_limit(temp_project_dir, monkeypatch)
    """Test that directory summaries respect size limits."""

```

## tests/test_summary/test_workflow_mapping.py
```python
def test_directory_mapping(temp_project_dir)
    """Test that .github/workflows maps to github/workflows."""

def test_workflow_summary_generation(temp_project_dir)
    """Test generation of workflow summaries in mapped location."""

def test_mixed_directory_handling(temp_project_dir)
    """Test handling of both workflow and non-workflow directories."""

```

## tests/test_tree_generator.py
```python
def mock_repo_with_files(mock_git_repo)
    """Extend mock_git_repo with additional test files"""

def test_ignore_patterns(mock_git_repo)
    """Test that ignore patterns work correctly"""

def test_full_tree_generation(mock_repo_with_files, monkeypatch)
    """Test complete tree generation with various file types"""

def test_empty_directory_handling(mock_git_repo)
    """Test handling of empty directories"""

def test_debug_path_processing(mock_repo_with_files)
    """Debug test to print path processing details"""

def debug_walk(path: Path, indent)

```

## tests/test_utils.py
```python
def test_get_project_root(temp_project_dir)
    """Test project root detection."""

def test_get_project_root_subfolder(temp_project_dir)
    """Test project root detection from subfolder."""

def test_load_config(temp_project_dir)
    """Test configuration loading."""

def test_load_config_missing()
    """Test loading missing configuration."""

```
