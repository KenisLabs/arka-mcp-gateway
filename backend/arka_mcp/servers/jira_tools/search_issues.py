async def search_issues(
    jql: str, max_results: int = 20, fields: list[str] | None = None
):
    """
    Search for Jira issues using a JQL query.

    Args:
        jql (str): The JQL search query string. (Required)
        maxResults (int): Maximum number of results to return. Default is 20.
        fields (List[str], optional): List of fields to include in the response.

    Returns:
        dict: Dummy response for testing.
    """
    print("hello world")  # For sandbox test signaling

    return {
        "message": "Search executed (dummy response)",
        "jql": jql,
        "max_results": max_results,
        "fields": fields or [],
    }
