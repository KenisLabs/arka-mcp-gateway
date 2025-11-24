from typing import Any, Optional

async def merge_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
    commit_title: Optional[str] = None,
    commit_message: Optional[str] = None,
    merge_method: Optional[str] = None,
    sha: Optional[str] = None,
) -> Any:
    """
    Merges an open pull request in a GitHub repository.

    Sends data to GitHub `/repos/{owner}/{repo}/pulls/{pull_number}/merge` endpoint.

    Args:
        owner: Repository owner's username or organization.
        repo: Repository name (without .git).
        pull_number: The number identifying the pull request.
        commit_title: Title for the merge commit.
        commit_message: Additional details for the merge commit message.
        merge_method: Merge strategy: 'merge', 'squash', or 'rebase'.
        sha: SHA of the pull request's head commit for safety.

    Returns:
        Parsed JSON response from the GitHub API, including merge result.

    Example:
        result = await merge_pull_request(
            owner="octocat",
            repo="Hello-World",
            pull_number=1347,
            commit_title="Merge feature",
            commit_message="Merging feature branch into main",
            merge_method="squash",
            sha="c5b97d5ae6c19d5c5df71a34c7fbeeda2479ccbc",
        )
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    endpoint = f"/repos/{owner}/{repo}/pulls/{pull_number}/merge"
    json_data: dict = {}
    if commit_title is not None:
        json_data["commit_title"] = commit_title
    if commit_message is not None:
        json_data["commit_message"] = commit_message
    if merge_method is not None:
        json_data["merge_method"] = merge_method
    if sha is not None:
        json_data["sha"] = sha
    return await client.put(endpoint, json_data)
