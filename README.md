## Development Guidelines

### Code Organization for LLM Interaction

When developing this project (or using it as a template), keep in mind these guidelines for effective collaboration with Large Language Models:

1. **Separation of Concerns**
   - Each package should have a single, clear responsibility
   - New features should be separate packages when appropriate
   - Avoid coupling between packages
   - Use consistent patterns across packages, but implement independently
   - Cross-cutting concerns should use shared conventions

2. **File Length and Modularity**
   - Keep files short and focused on a single responsibility
   - If you find yourself using comments like "... rest remains the same" or "... etc", the file is too long
   - Files should be completely replaceable in a single LLM interaction
   - Long files should be split into logical components

3. **Dependencies**
   - All dependencies managed in `pyproject.toml`
   - Optional dependencies grouped by feature:
     ```toml
     [project.optional-dependencies]
     test = ["pytest", ...]
     site = ["markdown2", ...]
     all = ["pytest", "markdown2", ...]  # Everything
     ```
   - Use appropriate groups during development:
     ```bash
     pip install -e ".[test]"  # Just testing
     pip install -e ".[all]"   # Everything
     ```

4. **Testing Standards**
   - Every new feature needs tests
   - Tests should be clear and focused
   - Use pytest fixtures for common setups
   - All workflows depend on tests passing
   - Test files should follow same modularity principles

5. **Why This Matters**
   - LLMs work best with clear, focused contexts
   - Complete file contents are better than partial updates with ellipsis
   - Tests provide clear examples of intended behavior
   - Shorter files make it easier for LLMs to:
     - Understand the complete context
     - Suggest accurate modifications
     - Maintain consistency
     - Avoid potential errors from incomplete information

7. **Best Practices**
   - Aim for files under 200 lines
   - Each file should have a single, clear purpose
   - Use directory structure to organize related components
   - Prefer many small files over few large files
   - Consider splitting when files require partial updates
   - Write tests alongside new features
   - Run tests locally before pushing

# LLM-Focused Summary System

## Overview
The project includes an automated summary generation system designed to help LLMs efficiently work with the codebase. This system generates both local directory summaries and project-wide summaries to provide focused, relevant context for different tasks.

## Types of Summaries

### Directory Summaries
Each directory in the project contains a `SUMMARY` file that concatenates all text files in that directory. This provides focused, local context when working on directory-specific tasks.

### Project-Wide Summaries
Special project-wide summaries are maintained in the `SUMMARIES/` directory on the `summaries` branch:

- `READMEs.md`: Concatenation of all README files in the project
- `README_SUBs.md`: Same as above but excluding the root README
- `PYTHON.md`: Structured view of all Python code including:
  - Function and class signatures
  - Type hints
  - Docstrings
  - Clear indication of class membership

## Accessing Summaries

### Directory Summaries
These are available on any branch in their respective directories:
```bash
# Example: View summary for the readme_generator package
cat src/readme_generator/SUMMARY
```

### Project-Wide Summaries
These live exclusively on the `summaries` branch:
```bash
# Switch to summaries branch
git checkout summaries

# View available summaries
ls SUMMARIES/
```

## Using Summaries Effectively

### For Local Development
Directory summaries are useful when:
- Getting up to speed on a specific package
- Understanding local code context
- Planning modifications to a package

### For Project-Wide Understanding
The `SUMMARIES/` directory helps with:
- Understanding overall project structure
- Finding relevant code across packages
- Reviewing API signatures and documentation
- Planning cross-package changes

### For LLM Interactions
- Point LLMs to specific summaries based on the task
- Use directory summaries for focused work
- Use project-wide summaries for architectural decisions
- Combine different summaries as needed for context

## Implementation Notes
- Summaries are automatically updated on every push to `main`
- The `summaries` branch is workflow-owned and force-pushed on updates
- Summary generation is configured in `pyproject.toml` under `[tool.summary]`
- Don't modify summaries directly - they're automatically generated

### Key Features

- Modular documentation system with Jinja2 templates
- Automatic project structure documentation
- Reusable GitHub Actions workflows
- Centralized configuration management
- Utility functions for common operations
- Clean, maintainable architecture optimized for AI agents
- Git operations handled through utilities