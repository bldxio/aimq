"""Tests for the git_loader module."""

import pytest

from aimq.commands.shared.git_loader import (
    GitURL,
    GitURLError,
    build_clone_url,
    get_cache_path,
    is_git_url,
    parse_git_url,
)


class TestGitURLParsing:
    """Test suite for git URL parsing."""

    def test_simple_github_url(self):
        """Test parsing simple user/repo format."""
        # Act
        result = parse_git_url("git:user/repo")

        # Assert
        assert result.host == "github.com"
        assert result.owner == "user"
        assert result.repo == "repo"
        assert result.ref is None
        assert result.subdir is None

    def test_url_with_branch(self):
        """Test parsing git URL with branch reference."""
        # Act
        result = parse_git_url("git:user/repo@main")

        # Assert
        assert result.host == "github.com"
        assert result.owner == "user"
        assert result.repo == "repo"
        assert result.ref == "main"
        assert result.subdir is None

    def test_url_with_subdirectory(self):
        """Test parsing git URL with subdirectory."""
        # Act
        result = parse_git_url("git:user/repo#services/worker")

        # Assert
        assert result.host == "github.com"
        assert result.owner == "user"
        assert result.repo == "repo"
        assert result.ref is None
        assert result.subdir == "services/worker"

    def test_url_with_branch_and_subdir(self):
        """Test parsing git URL with both branch and subdirectory."""
        # Act
        result = parse_git_url("git:user/repo@production#workers/tasks")

        # Assert
        assert result.host == "github.com"
        assert result.owner == "user"
        assert result.repo == "repo"
        assert result.ref == "production"
        assert result.subdir == "workers/tasks"

    def test_full_url_with_host(self):
        """Test parsing full git URL with custom host."""
        # Act
        result = parse_git_url("git:gitlab.com/user/repo@v1.0.0")

        # Assert
        assert result.host == "gitlab.com"
        assert result.owner == "user"
        assert result.repo == "repo"
        assert result.ref == "v1.0.0"
        assert result.subdir is None

    def test_repo_with_git_suffix(self):
        """Test parsing repo name with .git suffix."""
        # Act
        result = parse_git_url("git:user/repo.git")

        # Assert
        assert result.repo == "repo"

    def test_invalid_url_without_prefix(self):
        """Test error when URL doesn't start with git:"""
        # Act & Assert
        with pytest.raises(GitURLError, match="must start with 'git:'"):
            parse_git_url("user/repo")

    def test_invalid_url_format(self):
        """Test error when URL format is invalid."""
        # Act & Assert
        with pytest.raises(GitURLError, match="Invalid git URL format"):
            parse_git_url("git:invalid")

    def test_empty_components(self):
        """Test error when owner or repo is empty."""
        # Act & Assert
        with pytest.raises(GitURLError, match="must specify owner and repo"):
            parse_git_url("git://repo")


class TestBuildCloneURL:
    """Test suite for building clone URLs."""

    def test_build_https_url(self):
        """Test building HTTPS clone URL."""
        # Arrange
        git_url = GitURL(host="github.com", owner="user", repo="repo")

        # Act
        result = build_clone_url(git_url, use_ssh=False)

        # Assert
        assert result == "https://github.com/user/repo.git"

    def test_build_ssh_url(self):
        """Test building SSH clone URL."""
        # Arrange
        git_url = GitURL(host="github.com", owner="user", repo="repo")

        # Act
        result = build_clone_url(git_url, use_ssh=True)

        # Assert
        assert result == "git@github.com:user/repo.git"

    def test_build_url_custom_host(self):
        """Test building URL with custom host."""
        # Arrange
        git_url = GitURL(host="gitlab.com", owner="myorg", repo="myrepo")

        # Act
        result = build_clone_url(git_url, use_ssh=False)

        # Assert
        assert result == "https://gitlab.com/myorg/myrepo.git"


class TestCachePath:
    """Test suite for cache path generation."""

    def test_cache_path_unique_for_url(self):
        """Test that different URLs get different cache paths."""
        # Arrange
        url1 = GitURL(host="github.com", owner="user1", repo="repo1")
        url2 = GitURL(host="github.com", owner="user2", repo="repo2")

        # Act
        path1 = get_cache_path(url1)
        path2 = get_cache_path(url2)

        # Assert
        assert path1 != path2

    def test_cache_path_includes_ref(self):
        """Test that cache path is different for different refs."""
        # Arrange
        url1 = GitURL(host="github.com", owner="user", repo="repo", ref="main")
        url2 = GitURL(host="github.com", owner="user", repo="repo", ref="dev")

        # Act
        path1 = get_cache_path(url1)
        path2 = get_cache_path(url2)

        # Assert
        assert path1 != path2

    def test_cache_path_structure(self):
        """Test cache path structure."""
        # Arrange
        url = GitURL(host="github.com", owner="user", repo="repo")

        # Act
        path = get_cache_path(url)

        # Assert
        assert "aimq" in str(path)
        assert "git-cache" in str(path)
        assert path.is_absolute()


class TestIsGitURL:
    """Test suite for git URL detection."""

    def test_is_git_url_true(self):
        """Test detecting valid git URLs."""
        # Act & Assert
        assert is_git_url("git:user/repo")
        assert is_git_url("git:user/repo@main")
        assert is_git_url("git:host/user/repo#path")

    def test_is_git_url_false(self):
        """Test rejecting non-git URLs."""
        # Act & Assert
        assert not is_git_url("tasks.py")
        assert not is_git_url("/path/to/tasks.py")
        assert not is_git_url("https://github.com/user/repo")
        assert not is_git_url("")
