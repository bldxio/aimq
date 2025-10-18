"""Git repository loader for remote task files.

Supports npm-style git URLs for loading task files from remote repositories:
- git:user/repo - GitHub default branch
- git:user/repo@branch - Specific branch
- git:user/repo#path - Subdirectory in repo
- git:github.com/user/repo@tag - Full URL with version

Examples:
    git:mycompany/aimq-tasks
    git:mycompany/aimq-tasks@production
    git:mycompany/monorepo#services/worker
    git:github.com/mycompany/aimq-tasks@v1.0.0
"""

import hashlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class GitURL:
    """Parsed git URL components."""

    host: str  # github.com, gitlab.com, etc.
    owner: str  # username or organization
    repo: str  # repository name
    ref: Optional[str] = None  # branch, tag, or commit
    subdir: Optional[str] = None  # subdirectory path


class GitURLError(Exception):
    """Error parsing or processing git URL."""

    pass


def parse_git_url(url: str) -> GitURL:
    """Parse npm-style git URL into components.

    Args:
        url: Git URL in format git:user/repo, git:user/repo@ref, git:host/user/repo#path

    Returns:
        GitURL with parsed components

    Raises:
        GitURLError: If URL format is invalid

    Examples:
        >>> parse_git_url("git:user/repo")
        GitURL(host='github.com', owner='user', repo='repo', ref=None, subdir=None)

        >>> parse_git_url("git:user/repo@main")
        GitURL(host='github.com', owner='user', repo='repo', ref='main', subdir=None)

        >>> parse_git_url("git:user/repo#workers/tasks")
        GitURL(host='github.com', owner='user', repo='repo', ref=None, subdir='workers/tasks')

        >>> parse_git_url("git:gitlab.com/user/repo@v1.0.0")
        GitURL(host='gitlab.com', owner='user', repo='repo', ref='v1.0.0', subdir=None)
    """
    if not url.startswith("git:"):
        raise GitURLError(f"Git URL must start with 'git:': {url}")

    # Remove 'git:' prefix
    url = url[4:]

    # Extract subdirectory if present (after #)
    subdir = None
    if "#" in url:
        url, subdir = url.split("#", 1)

    # Extract ref if present (after @)
    ref = None
    if "@" in url:
        url, ref = url.split("@", 1)

    # Parse host/owner/repo
    # Supports: user/repo OR host/user/repo
    parts = url.split("/")

    if len(parts) == 2:
        # git:user/repo (default to github.com)
        host = "github.com"
        owner, repo = parts
    elif len(parts) == 3:
        # git:host/user/repo
        host, owner, repo = parts
    else:
        raise GitURLError(
            f"Invalid git URL format. Expected 'user/repo' or 'host/user/repo': {url}"
        )

    # Validate components
    if not owner or not repo:
        raise GitURLError(f"Git URL must specify owner and repo: {url}")

    # Remove .git suffix if present
    if repo.endswith(".git"):
        repo = repo[:-4]

    return GitURL(host=host, owner=owner, repo=repo, ref=ref, subdir=subdir)


def build_clone_url(git_url: GitURL, use_ssh: bool = False) -> str:
    """Build a full git clone URL from parsed components.

    Args:
        git_url: Parsed GitURL object
        use_ssh: If True, use SSH URL format (git@host:owner/repo)
                 If False, use HTTPS URL format (https://host/owner/repo)

    Returns:
        Full git clone URL

    Examples:
        >>> url = parse_git_url("git:user/repo")
        >>> build_clone_url(url, use_ssh=False)
        'https://github.com/user/repo.git'

        >>> build_clone_url(url, use_ssh=True)
        'git@github.com:user/repo.git'
    """
    if use_ssh:
        return f"git@{git_url.host}:{git_url.owner}/{git_url.repo}.git"
    else:
        return f"https://{git_url.host}/{git_url.owner}/{git_url.repo}.git"


def get_cache_path(git_url: GitURL) -> Path:
    """Get cache directory path for a git repository.

    Args:
        git_url: Parsed GitURL object

    Returns:
        Path to cache directory

    Note:
        Cache key includes host, owner, repo, and ref to ensure different
        versions are cached separately.
    """
    # Create cache key from URL components
    cache_key = f"{git_url.host}/{git_url.owner}/{git_url.repo}"
    if git_url.ref:
        cache_key += f"@{git_url.ref}"

    # Hash the cache key to create a filesystem-safe directory name
    cache_hash = hashlib.sha256(cache_key.encode()).hexdigest()[:16]

    # Use system temp directory for cache
    cache_dir = Path(tempfile.gettempdir()) / "aimq" / "git-cache" / cache_hash
    return cache_dir


def clone_or_update_repo(git_url: GitURL, use_ssh: bool = False) -> Path:
    """Clone or update a git repository to the cache.

    Args:
        git_url: Parsed GitURL object
        use_ssh: If True, use SSH for cloning

    Returns:
        Path to the cloned repository

    Raises:
        GitURLError: If clone/update fails
    """
    cache_path = get_cache_path(git_url)
    clone_url = build_clone_url(git_url, use_ssh=use_ssh)

    try:
        if cache_path.exists():
            # Repository already cached, update it
            # Check if it's a git repo
            if not (cache_path / ".git").exists():
                # Cache corrupted, remove and re-clone
                shutil.rmtree(cache_path)
                return _clone_fresh(clone_url, cache_path, git_url.ref)

            # Update existing clone
            subprocess.run(
                ["git", "fetch", "--all"],
                cwd=cache_path,
                check=True,
                capture_output=True,
                text=True,
            )

            # Checkout the specified ref (or default branch)
            if git_url.ref:
                subprocess.run(
                    ["git", "checkout", git_url.ref],
                    cwd=cache_path,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                subprocess.run(
                    ["git", "pull"],
                    cwd=cache_path,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            else:
                # Get default branch and checkout
                result = subprocess.run(
                    ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                    cwd=cache_path,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    default_branch = result.stdout.strip().split("/")[-1]
                    subprocess.run(
                        ["git", "checkout", default_branch],
                        cwd=cache_path,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    subprocess.run(
                        ["git", "pull"],
                        cwd=cache_path,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
        else:
            # Clone fresh
            return _clone_fresh(clone_url, cache_path, git_url.ref)

    except subprocess.CalledProcessError as e:
        stderr = e.stderr if hasattr(e, "stderr") else str(e)
        raise GitURLError(f"Git operation failed: {stderr}")

    return cache_path


def _clone_fresh(clone_url: str, cache_path: Path, ref: Optional[str] = None) -> Path:
    """Clone a fresh copy of the repository.

    Args:
        clone_url: Full git clone URL
        cache_path: Where to clone to
        ref: Optional branch/tag to checkout

    Returns:
        Path to cloned repository

    Raises:
        GitURLError: If clone fails
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Clone the repository
        cmd = ["git", "clone"]
        if ref:
            cmd.extend(["--branch", ref])
        cmd.extend([clone_url, str(cache_path)])

        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr if hasattr(e, "stderr") else str(e)
        raise GitURLError(f"Git clone failed: {stderr}")

    return cache_path


def find_tasks_file(repo_path: Path, subdir: Optional[str] = None) -> Path:
    """Find tasks.py in the cloned repository.

    Args:
        repo_path: Path to cloned repository
        subdir: Optional subdirectory to search in

    Returns:
        Path to tasks.py file

    Raises:
        GitURLError: If tasks.py not found
    """
    # Determine search path
    if subdir:
        search_path = repo_path / subdir
        if not search_path.exists():
            raise GitURLError(f"Subdirectory not found: {subdir}")
    else:
        search_path = repo_path

    # Look for tasks.py
    tasks_file = search_path / "tasks.py"
    if not tasks_file.exists():
        raise GitURLError(
            f"tasks.py not found in {search_path.relative_to(repo_path) or 'repository root'}"
        )

    return tasks_file


def load_from_git_url(url: str, use_ssh: bool = False) -> Path:
    """Load a tasks.py file from a git URL.

    Args:
        url: Git URL in npm style (git:user/repo, git:user/repo@branch, etc.)
        use_ssh: If True, use SSH for git operations

    Returns:
        Path to the tasks.py file

    Raises:
        GitURLError: If URL is invalid or loading fails

    Examples:
        >>> load_from_git_url("git:mycompany/aimq-tasks")
        Path('/tmp/aimq/git-cache/abc123/tasks.py')

        >>> load_from_git_url("git:mycompany/monorepo#services/worker")
        Path('/tmp/aimq/git-cache/def456/services/worker/tasks.py')
    """
    # Parse the git URL
    git_url = parse_git_url(url)

    # Clone or update the repository
    repo_path = clone_or_update_repo(git_url, use_ssh=use_ssh)

    # Find the tasks.py file
    tasks_file = find_tasks_file(repo_path, git_url.subdir)

    return tasks_file


def is_git_url(path_or_url: str) -> bool:
    """Check if a string is a git URL.

    Args:
        path_or_url: String that might be a git URL

    Returns:
        True if string starts with 'git:', False otherwise

    Examples:
        >>> is_git_url("git:user/repo")
        True

        >>> is_git_url("tasks.py")
        False

        >>> is_git_url("/path/to/tasks.py")
        False
    """
    return path_or_url.startswith("git:")
