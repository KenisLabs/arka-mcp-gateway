from typing import Any, Optional

async def create_pull_request(
    owner: str,
    repo: str,
    head: str,
    base: str,
    title: Optional[str] = None,
    body: Optional[str] = None,
    draft: Optional[bool] = None,
    issue: Optional[int] = None,
    maintainer_can_modify: Optional[bool] = None,
    head_repo: Optional[str] = None,
) -> Any:
    """
    Creates a pull request in a GitHub repository.

    Sends data to GitHub `/repos/{owner}/{repo}/pulls` endpoint.

    Args:
        owner: Repository owner's username or organization.
        repo: Repository name (without .git).
        head: The name of the branch where changes are implemented (e.g., 'feature-branch' or 'user:feature-branch').
        base: The name of the branch you want the changes pulled into (e.g., 'main').
        title: Title for the new pull request; required if `issue` is not set.
        body: Detailed description or contents of the pull request.
        draft: Whether to create the PR as a draft.
        issue: Issue number to convert into a PR; optional if `title` is provided.
        maintainer_can_modify: Allow maintainers to modify the PR.
        head_repo: Full repo name for cross-repository PRs (owner/repo); optional.

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await create_pull_request(
            owner="octocat",
            repo="Hello-World",
            head="feature-branch",
            base="main",
            title="Add new feature",
            body="This PR adds a new feature.",
            draft=False,
            maintainer_can_modify=True,
        )
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    endpoint = f"/repos/{owner}/{repo}/pulls"
    json_data: dict = {"head": head, "base": base}
    if title is not None:
        json_data["title"] = title
    if body is not None:
        json_data["body"] = body
    if draft is not None:
        json_data["draft"] = draft
    if issue is not None:
        json_data["issue"] = issue
    if maintainer_can_modify is not None:
        json_data["maintainer_can_modify"] = maintainer_can_modify
    if head_repo is not None:
        json_data["head_repo"] = head_repo
    return await client.post(endpoint, json_data)
