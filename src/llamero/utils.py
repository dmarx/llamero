from pathlib import Path
import tomli
import os
import subprocess
from loguru import logger

def get_project_root() -> Path:
    """
    Get the project root directory by looking for pyproject.toml
    Returns the absolute path to the project root
    """
    current = Path.cwd().absolute()
    
    # Look for pyproject.toml in current and parent directories
    while current != current.parent:
        if (current / 'pyproject.toml').exists():
            return current
        current = current.parent
    
    # If we couldn't find it, use the current working directory
    # and log a warning
    logger.warning("Could not find pyproject.toml in parent directories")
    return Path.cwd().absolute()

def load_config(config_path: str) -> dict:
    """
    Load configuration from a TOML file
    
    Args:
        config_path (str): Path to the TOML configuration file relative to project root
        
    Returns:
        dict: Parsed configuration data
    """

    full_path = get_project_root() / config_path
    if full_path.exists():
        logger.debug(f"Attempting to load config from: {full_path}")
        with open(full_path, "rb") as f:
            return tomli.load(f)
    else:
        #logger.error(f"Configuration file not found: {full_path}")
        raise FileNotFoundError(f"Configuration file not found: {full_path}")

def commit_and_push(files_to_commit: str|Path|list[str]|list[Path], message = None):
    """Commit and push changes for a specific file"""
    if isinstance(files_to_commit, str) or isinstance(files_to_commit, Path):
        files_to_commit = [files_to_commit]
    files_to_commit = [str(f) for f in files_to_commit] # Ensure Path objects are stringified
    logger.info(f"files to commit: {files_to_commit}")
    try:
        # Configure Git for GitHub Actions
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "action@github.com"], check=True)

        #changes = False
        files_staged = []
        for file_to_commit in files_to_commit:
            # Check if there are any changes to commit
            status = subprocess.run(["git", "status", "--porcelain", file_to_commit], capture_output=True, text=True, check=True)
            if status.stdout.strip():
                #changes=True
                subprocess.run(["git", "add", file_to_commit], check=True)
                files_staged.append(file_to_commit)
        if not files_staged:
            logger.info(f"No changes to commit")
            return
        if message is None:
            if len(files_staged) == 1:
                message = f"Update {file_to_commit}"
            else:
                message = f"Updated {len(files_staged)} files."
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push"], check=True)
        
        logger.success(f"Changes to {files_staged} committed and pushed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during git operations: {e}")
        if "nothing to commit" in str(e):
            logger.info("No changes to commit. Continuing execution")
        else:
            logger.warning("Exiting early due to Git error")
            raise

def commit_and_push_to_branch(
    message: str,
    branch: str,
    paths: list[str | Path],
    base_branch: str | None = None,
    force: bool = False
) -> None:
    """Commit changes and push to specified branch.
    
    Args:
        message: Commit message
        branch: Branch to push to
        paths: List of paths to commit
        base_branch: Optional base branch to create new branch from
        force: If True, create fresh branch and force push (for generated content)
    """
    # Convert paths to strings
    path_strs = [str(p) for p in paths]
    
    # Set up git config
    subprocess.run(["git", "config", "--local", "user.email", "github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "config", "--local", "user.name", "github-actions[bot]"])
    
    if force:
        # Create fresh branch from base_branch or HEAD
        base = base_branch or "HEAD"
        logger.info(f"Creating fresh branch {branch} from {base}")
        subprocess.run(["git", "checkout", "-B", branch, base])
    else:
        # Normal branch handling
        if base_branch:
            logger.info(f"Creating new branch {branch} from {base_branch}")
            subprocess.run(["git", "checkout", "-b", branch, base_branch])
        else:
            logger.info(f"Switching to branch {branch}")
            subprocess.run(["git", "checkout", "-b", branch])
            subprocess.run(["git", "pull", "origin", branch], capture_output=True)
    
    # Stage and commit changes
    subprocess.run(["git", "add", *path_strs])
    
    # Only commit if there are changes
    result = subprocess.run(
        ["git", "diff", "--staged", "--quiet"],
        capture_output=True
    )
    if result.returncode == 1:  # Changes exist
        logger.info("Committing changes")
        subprocess.run(["git", "commit", "-m", message])
        
        # Push changes
        if force:
            logger.info(f"Force pushing {branch} branch")
            subprocess.run(["git", "push", "-f", "origin", branch])
        else:
            logger.info("Pushing changes")
            subprocess.run(["git", "push", "origin", branch])
    else:
        logger.info("No changes to commit")
