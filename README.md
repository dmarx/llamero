![llamero logo](assets/llamero-logo.jpg)

# llamero

## Introduction

Llamero is a toolkit to facilitate collaborating with LLMs on coding projects. It provides tools for:

- Generating structured documentation and summaries to provide LLMs with relevant context
- Maintaining clean, LLM-friendly project organization
- Automating common documentation tasks
- Building modular, context-aware codebases
- Github actions integrations
### Key Features

- Modular documentation system with Jinja2 templates
- Automatic project structure documentation
- Reusable GitHub Actions workflows
- Centralized configuration management
- Utility functions for common operations
- Clean, maintainable architecture optimized for AI agents
- Git operations handled through utilities
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
     ```
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
   - Syntax permitting, files should begin with a comment indicating that file's name and relative path from the project root
## LLM-Focused Summary System

One of the most valuable features `llamero` offers is tooling to automate generation of various kinds of project/directory summaries that can be provided to an LLM for context.

This system generates both local directory summaries and project-wide summaries to provide focused, relevant context for different tasks.

The default behavior is to generate summaries and force push them to a dedicated `summaries` branch, keeping the actual project uncluttered so the user can pick and choose 
the specific summaries to share as they need to, when they need to, rather than filling up the LLMs context unnecessarily.

For a concrete example, poke around [llamero's `summaries` branch](https://github.com/dmarx/llamero/tree/summaries).
`llamero`'s summaries are currently configured to only be generated on request, through the `on: workflow_dispatch:` directive in the workflow configuration [here](https://github.com/dmarx/llamero/blob/main/.github/workflows/generate_summaries.yaml).

### Directory Summaries

Each directory in the project contains a `SUMMARY` file that concatenates all text files in that directory, recursively. 
This provides focused, local context when working on directory-specific tasks.

### Project-Wide Summaries
Special project-wide summaries are maintained in the `SUMMARIES/` directory:

- `READMEs.md`: Concatenation of all README files in the project
- `README_SUBs.md`: Same as above but excluding the root README
- `PYTHON.md`: Structured view of all Python code including:
  - Function and class signatures
  - Type hints
  - Docstrings
  - Clear indication of class membership


```bash
# Switch to summaries branch
git checkout summaries

# View available summaries
ls SUMMARIES/
```
## Project Structure

```

├── .github
│   └── workflows
│       ├── build_readme.yml
│       ├── generate_summaries.yaml
│       ├── publish.yaml
│       └── test.yml
├── LICENSE
├── README.md
├── assets
│   └── llamero-logo.jpg
├── build
│   └── lib
│       └── llamero
│           ├── __init__.py
│           ├── __main__.py
│           ├── dir2doc.py
│           ├── summary
│           │   ├── __init__.py
│           │   ├── concatenative.py
│           │   ├── python_files.py
│           │   ├── python_signatures.py
│           │   └── readmes.py
│           ├── tree_generator.py
│           └── utils.py
├── docs
│   └── readme
│       ├── base.md.j2
│       └── sections
│           ├── config.md.j2
│           ├── development.md.j2
│           ├── features.md.j2
│           ├── introduction.md.j2
│           ├── structure.md.j2
│           └── summaries.md.j2
├── pyproject.toml
├── src
│   └── llamero
│       ├── __init__.py
│       ├── __main__.py
│       ├── dir2doc.py
│       ├── summary
│       │   ├── __init__.py
│       │   ├── concatenative.py
│       │   ├── python_files.py
│       │   ├── python_signatures.py
│       │   └── readmes.py
│       ├── tree_generator.py
│       └── utils.py
└── tests
    ├── conftest.py
    ├── test_dir2doc.py
    ├── test_summary
    │   ├── test_concatenative.py
    │   ├── test_python_signatures.py
    │   ├── test_size_limits.py
    │   └── test_workflow_mapping.py
    ├── test_tree_generator.py
    └── test_utils.py

```
