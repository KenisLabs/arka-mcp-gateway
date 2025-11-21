"""
Utility functions for Notion MCP tools.

Helper functions for extracting and processing data from Notion API responses.
"""
from typing import Dict, Any, Optional, List


def extract_title(notion_object: Dict[str, Any]) -> str:
    """
    Extract title from a Notion page or database object.

    Handles the complex nested structure of Notion title properties and provides
    a fallback to "Untitled" if the title cannot be extracted.

    Args:
        notion_object: A Notion page or database object from the API

    Returns:
        The extracted title string, or "Untitled" if not found

    Example:
        result = await search(query="project")
        for item in result.get("results", []):
            title = extract_title(item)
            print(f"Found: {title}")
    """
    try:
        properties = notion_object.get('properties', {})

        # Try 'title' property first (common for pages)
        if 'title' in properties:
            title_prop = properties['title']
            if title_prop.get('type') == 'title' and title_prop.get('title'):
                title_array = title_prop['title']
                if title_array and len(title_array) > 0:
                    return title_array[0].get('plain_text', 'Untitled')

        # Try 'Name' property (common for database rows)
        if 'Name' in properties:
            name_prop = properties['Name']
            if name_prop.get('type') == 'title' and name_prop.get('title'):
                title_array = name_prop['title']
                if title_array and len(title_array) > 0:
                    return title_array[0].get('plain_text', 'Untitled')

        # Try any property with type 'title'
        for prop_name, prop_value in properties.items():
            if isinstance(prop_value, dict) and prop_value.get('type') == 'title':
                title_array = prop_value.get('title', [])
                if title_array and len(title_array) > 0:
                    return title_array[0].get('plain_text', 'Untitled')

        return "Untitled"

    except (KeyError, IndexError, TypeError, AttributeError):
        return "Untitled"


def extract_plain_text(rich_text_array: List[Dict[str, Any]]) -> str:
    """
    Extract plain text from Notion rich text array.

    Args:
        rich_text_array: Array of rich text objects from Notion API

    Returns:
        Combined plain text string

    Example:
        content = extract_plain_text(block['paragraph']['rich_text'])
    """
    try:
        if not rich_text_array:
            return ""

        text_parts = []
        for text_obj in rich_text_array:
            if isinstance(text_obj, dict):
                plain_text = text_obj.get('plain_text', '')
                if not plain_text:
                    # Fallback to text.content
                    text_content = text_obj.get('text', {}).get('content', '')
                    plain_text = text_content
                text_parts.append(plain_text)

        return ''.join(text_parts)

    except (TypeError, AttributeError):
        return ""


def extract_url(notion_object: Dict[str, Any]) -> Optional[str]:
    """
    Extract URL from a Notion page or database object.

    Args:
        notion_object: A Notion page or database object from the API

    Returns:
        The URL string, or None if not found

    Example:
        result = await get_page(block_id="page-id")
        url = extract_url(result)
    """
    try:
        return notion_object.get('url')
    except (AttributeError, TypeError):
        return None


def extract_id(notion_object: Dict[str, Any]) -> Optional[str]:
    """
    Extract ID from a Notion object.

    Args:
        notion_object: A Notion object from the API

    Returns:
        The ID string, or None if not found

    Example:
        result = await search(query="project")
        for item in result.get("results", []):
            item_id = extract_id(item)
    """
    try:
        return notion_object.get('id')
    except (AttributeError, TypeError):
        return None


def extract_object_type(notion_object: Dict[str, Any]) -> Optional[str]:
    """
    Extract object type from a Notion object.

    Args:
        notion_object: A Notion object from the API

    Returns:
        The object type ("page", "database", "block", etc.), or None if not found

    Example:
        result = await search(query="project")
        for item in result.get("results", []):
            obj_type = extract_object_type(item)
            if obj_type == "page":
                print(f"Found page: {extract_title(item)}")
    """
    try:
        return notion_object.get('object')
    except (AttributeError, TypeError):
        return None


def format_search_results(search_response: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Format search results into a simple list with id, title, type, and url.

    Args:
        search_response: Response from search() or fetch_data() function

    Returns:
        List of simplified result objects

    Example:
        results = await search(query="project")
        formatted = format_search_results(results)
        for item in formatted:
            print(f"{item['type']}: {item['title']} ({item['url']})")
    """
    try:
        results = search_response.get('results', [])
        formatted = []

        for item in results:
            formatted.append({
                'id': extract_id(item) or '',
                'title': extract_title(item),
                'type': extract_object_type(item) or 'unknown',
                'url': extract_url(item) or ''
            })

        return formatted

    except (AttributeError, TypeError, KeyError):
        return []


def extract_property_value(properties: Dict[str, Any], property_name: str) -> Any:
    """
    Extract value from a specific property in a Notion page/database row.

    Handles different property types and returns the actual value.

    Args:
        properties: The properties dict from a Notion page object
        property_name: Name of the property to extract

    Returns:
        The property value, type depends on property type

    Example:
        page = await get_page(block_id="page-id")
        status = extract_property_value(page['properties'], 'Status')
        due_date = extract_property_value(page['properties'], 'Due Date')
    """
    try:
        if property_name not in properties:
            return None

        prop = properties[property_name]
        prop_type = prop.get('type')

        if prop_type == 'title':
            title_array = prop.get('title', [])
            return extract_plain_text(title_array)

        elif prop_type == 'rich_text':
            rich_text_array = prop.get('rich_text', [])
            return extract_plain_text(rich_text_array)

        elif prop_type == 'number':
            return prop.get('number')

        elif prop_type == 'select':
            select_obj = prop.get('select')
            return select_obj.get('name') if select_obj else None

        elif prop_type == 'multi_select':
            multi_select_array = prop.get('multi_select', [])
            return [item.get('name') for item in multi_select_array]

        elif prop_type == 'date':
            date_obj = prop.get('date')
            if date_obj:
                return {
                    'start': date_obj.get('start'),
                    'end': date_obj.get('end')
                }
            return None

        elif prop_type == 'checkbox':
            return prop.get('checkbox')

        elif prop_type == 'url':
            return prop.get('url')

        elif prop_type == 'email':
            return prop.get('email')

        elif prop_type == 'phone_number':
            return prop.get('phone_number')

        elif prop_type == 'status':
            status_obj = prop.get('status')
            return status_obj.get('name') if status_obj else None

        # For other types, return the raw property object
        return prop

    except (AttributeError, TypeError, KeyError):
        return None
