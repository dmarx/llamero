# tests/test_summary/test_concatenative.py
import pytest
from pathlib import Path
from llamero.summary.concatenative import SummaryGenerator

@pytest.fixture
def config_project_dir(temp_project_dir):
    """Create a project directory with custom configuration."""
    config_content = """
[project]
name = "test-project"
description = "Test project"
version = "0.1.0"

[tool.summary]
max_file_size_kb = 10
exclude_patterns = [
    '.hidden',
    'excluded_file.txt',
    'temp'
]
include_extensions = [
    '.py',
    '.md',
    '.txt',
    '.custom'
]
exclude_directories = [
    'excluded_dir',
    'temp_dir',
    'data'
]
"""
    (temp_project_dir / "pyproject.toml").write_text(config_content)
    return temp_project_dir

@pytest.fixture
def workflow_project_dir(temp_project_dir):
    """Create a project directory with workflow files."""
    # Create workflow file
    workflow_dir = temp_project_dir / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "test.yml").write_text("name: Test")
    
    # Add basic pyproject.toml
    config_content = """
[project]
name = "test-project"
description = "Test project"
version = "0.1.0"
"""
    (temp_project_dir / "pyproject.toml").write_text(config_content)
    return temp_project_dir

@pytest.fixture
def test_files(config_project_dir):
    """Create a set of test files with various extensions and patterns."""
    # Create test files
    files = {
        # Should be included
        'test.py': 'print("Hello")',
        'doc.md': '# Documentation',
        'notes.txt': 'Some notes',
        'special.custom': 'Custom file',
        'nested/test.py': 'nested = True',
        
        # Should be excluded by pattern
        '.hidden/secret.txt': 'secret',
        'excluded_file.txt': 'excluded',
        'temp/data.py': 'temp data',
        
        # Should be excluded by extension
        'script.sh': '#!/bin/bash',
        'data.csv': 'a,b,c',
        
        # Should be excluded by directory
        'excluded_dir/test.py': 'excluded',
        'temp_dir/data.txt': 'temp',
        
        # Should be excluded by size (if >10KB)
        'large.py': 'x' * (11 * 1024)  # 11KB
    }
    
    for path, content in files.items():
        file_path = config_project_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        
    return config_project_dir

def test_config_loading(config_project_dir):
    """Test that configuration is properly loaded from pyproject.toml."""
    generator = SummaryGenerator(config_project_dir)
    
    assert generator.max_file_size == 10 * 1024
    assert '.hidden' in generator.config['exclude_patterns']
    assert '.custom' in generator.config['include_extensions']
    assert 'excluded_dir' in generator.config['exclude_directories']

def test_file_inclusion_by_extension(test_files):
    """Test that files are correctly included/excluded based on extension."""
    generator = SummaryGenerator(test_files)
    
    # Should include
    assert generator.should_include_file(test_files / 'test.py')
    assert generator.should_include_file(test_files / 'doc.md')
    assert generator.should_include_file(test_files / 'special.custom')
    
    # Should exclude
    assert not generator.should_include_file(test_files / 'script.sh')
    assert not generator.should_include_file(test_files / 'data.csv')

def test_file_exclusion_by_pattern(test_files):
    """Test that files are correctly excluded based on patterns."""
    generator = SummaryGenerator(test_files)
    
    # Should exclude
    assert not generator.should_include_file(test_files / '.hidden/secret.txt')
    assert not generator.should_include_file(test_files / 'excluded_file.txt')
    assert not generator.should_include_file(test_files / 'temp/data.py')

def test_directory_exclusion(test_files):
    """Test that directories are correctly excluded."""
    generator = SummaryGenerator(test_files)
    
    # Should exclude
    assert not generator.should_include_directory(test_files / 'excluded_dir')
    assert not generator.should_include_directory(test_files / 'temp_dir')
    
    # Should include
    assert generator.should_include_directory(test_files / 'nested')

def test_file_size_limits(test_files):
    """Test that files are excluded based on size limits."""
    generator = SummaryGenerator(test_files)
    
    # Small file should be included
    assert generator.should_include_file(test_files / 'test.py')
    
    # Large file should be excluded
    assert not generator.should_include_file(test_files / 'large.py')

def test_summary_generation_with_config(test_files):
    """Test that summary generation respects all configuration settings."""
    generator = SummaryGenerator(test_files)
    summary_files = generator.generate_all_summaries()
    
    # Get all generated summaries
    summaries = {}
    for summary_file in summary_files:
        summaries[summary_file] = summary_file.read_text()
    
    # Check that the right files were included
    root_summary = test_files / 'SUMMARY'
    if root_summary in summaries:
        content = summaries[root_summary]
        
        # Should include
        assert 'File: test.py' in content
        assert 'File: doc.md' in content
        assert 'File: special.custom' in content
        
        # Should exclude
        assert 'excluded_file.txt' not in content
        assert 'secret.txt' not in content
        assert 'script.sh' not in content
        assert 'large.py' not in content

def test_nested_directory_handling(test_files):
    """Test that nested directories are handled correctly."""
    generator = SummaryGenerator(test_files)
    summary_files = generator.generate_all_summaries()
    
    # Check nested directory summary
    nested_summary = test_files / 'nested' / 'SUMMARY'
    assert nested_summary.exists()
    content = nested_summary.read_text()
    
    assert 'File: nested/test.py' in content
    assert 'nested = True' in content

def test_default_config_fallback(temp_project_dir):
    """Test that default configuration is used when no config file exists."""
    # Create a test.py file
    (temp_project_dir / "test.py").write_text("print('test')")
    
    generator = SummaryGenerator(temp_project_dir)
    
    # Check default extensions
    assert generator.should_include_file(temp_project_dir / "test.py")
    
    # Create files with extensions that should be excluded by default
    test_sh = temp_project_dir / "script.sh"
    test_sh.write_text("#!/bin/bash")
    assert not generator.should_include_file(test_sh)
    
    # Check default directory exclusions
    git_dir = temp_project_dir / ".git"
    git_dir.mkdir(exist_ok=True)
    assert not generator.should_include_directory(git_dir)

def test_workflow_directory_mapping(workflow_project_dir):
    """Test that .github/workflows is correctly mapped to github/workflows."""
    generator = SummaryGenerator(workflow_project_dir)
    
    # Add a workflow file
    workflow_dir = workflow_project_dir / ".github" / "workflows"
    (workflow_dir / "test.yml").write_text("name: Test")
    
    summary_files = generator.generate_all_summaries()
    
    # Check that workflow summary was created in mapped location
    mapped_summary = workflow_project_dir / "github" / "workflows" / "SUMMARY"
    assert mapped_summary in summary_files
    
    # Verify content references original path
    content = mapped_summary.read_text()
    assert "File: .github/workflows/test.yml" in content

def test_error_handling(config_project_dir, caplog):
    """Test error handling for unreadable files."""
    caplog.set_level("ERROR")
    
    # Create unreadable file
    bad_file = config_project_dir / "unreadable.py"
    bad_file.write_text("test")
    
    try:
        # Make file unreadable
        bad_file.chmod(0o000)
        
        generator = SummaryGenerator(config_project_dir)
        generator.generate_directory_summary(config_project_dir)
        
        # Check for error message
        for record in caplog.records:
            if (
                record.levelname == "ERROR" 
                and "Error processing" in record.message 
                and "Permission denied" in record.message
            ):
                break
        else:
            pytest.fail("Expected error message not found in logs")
            
    finally:
        # Clean up
        bad_file.chmod(0o644)
        bad_file.unlink()

def test_excluded_directory_files(test_files):
    """Test that files in excluded directories are excluded regardless of extension."""
    # Create a file with valid extension in excluded directory
    excluded_dir = test_files / "data"
    excluded_dir.mkdir(exist_ok=True)
    test_file = excluded_dir / "test.py"
    test_file.write_text("print('should be excluded')")
    
    generator = SummaryGenerator(test_files)
    
    # File should be excluded because it's in an excluded directory
    assert not generator.should_include_file(test_file)
    
    # Generate summary and verify file is not included
    summaries = generator.generate_all_summaries()
    for summary_file in summaries:
        content = summary_file.read_text()
        assert "test.py" not in content
        assert "should be excluded" not in content
