import asyncio
import json
import os
import logging
import httpx
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("raindrop-mcp")

# Constants
API_URL = "https://api.raindrop.io/rest/v1"

# Create FastMCP server
mcp = FastMCP("Raindrop Collections API")

# Helper function to get headers with authentication token
async def get_headers():
    # Get token from .env file
    token = os.getenv("RAINDROP_TOKEN")
    if not token:
        logger.warning("RAINDROP_TOKEN not found in .env file.")
        logger.warning("Please add your Raindrop API token to the .env file.")
    
    # Use proper Bearer token format for authorization
    return {
        "Authorization": f"Bearer {token}" if token else "",
        "Content-Type": "application/json"
    }

# Define tools
@mcp.tool("get_root_collections")
async def get_root_collections() -> list:
    """
    Get all root collections from Raindrop.io
    """
    # Fetch collections from root endpoint
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        raise ValueError("API token not set. Please check your .env file.")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/collections", headers=headers)
            
            if response.status_code != 200:
                raise ValueError(f"API returned status {response.status_code}")
            
            data = response.json()
            
            if "items" not in data:
                raise ValueError("Unexpected API response format")
            
            # Format response - return native Python list
            return [
                {
                    "_id": c.get("_id", ""),
                    "title": c.get("title", ""),
                    "count": c.get("count", 0),
                    "public": c.get("public", False),
                    "view": c.get("view", ""),
                    "color": c.get("color", ""),
                    "created": c.get("created", ""),
                    "lastUpdate": c.get("lastUpdate", ""),
                    "expanded": c.get("expanded", False)
                }
                for c in data["items"]
            ]
    except Exception as e:
        raise ValueError(f"Error fetching root collections: {str(e)}")

@mcp.tool("get_child_collections")
async def get_child_collections() -> str:
    """
    Get all child collections from Raindrop.io
    """
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        return json.dumps({
            "isError": True,
            "content": [{"type": "text", "text": "API token not set. Please check your .env file."}]
        })
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/collections/childrens", headers=headers)
            
            if response.status_code != 200:
                return json.dumps({
                    "isError": True,
                    "content": [{"type": "text", "text": f"Error: API returned status {response.status_code}"}]
                })
            
            data = response.json()
            
            if "items" not in data:
                return json.dumps({
                    "isError": True,
                    "content": [{"type": "text", "text": "Error: Unexpected API response format"}]
                })
            
            # Format response
            result = [
                {
                    "_id": c.get("_id", ""),
                    "title": c.get("title", ""),
                    "count": c.get("count", 0),
                    "public": c.get("public", False),
                    "view": c.get("view", ""),
                    "color": c.get("color", ""),
                    "parent_id": c.get("parent", {}).get("$id", None),
                    "created": c.get("created", ""),
                    "lastUpdate": c.get("lastUpdate", ""),
                    "expanded": c.get("expanded", False)
                }
                for c in data["items"]
            ]
            
            return json.dumps({
                "content": [
                    {"type": "text", "text": f"Found {len(result)} child collection(s)"},
                    {"type": "json", "json": result}
                ]
            })
    except Exception as e:
        return json.dumps({
            "isError": True,
            "content": [{"type": "text", "text": f"Error: {str(e)}"}]
        })

@mcp.tool("get_collection_by_id")
async def get_collection_by_id(collection_id: int) -> dict:
    """
    Get a specific collection from Raindrop.io by ID
    
    Args:
        collection_id: ID of the collection to fetch
    """
    # Validate input
    if collection_id is None:
        raise ValueError("No collection ID provided")
    
    # Fetch specific collection by ID
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        raise ValueError("API token not set. Please check your .env file.")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/collection/{collection_id}", headers=headers)
            
            if response.status_code != 200:
                raise ValueError(f"API returned status {response.status_code}")
            
            data = response.json()
            
            if "item" not in data:
                raise ValueError("Unexpected API response format")
            
            # Format the single collection response
            collection = data["item"]
            result = {
                "_id": collection.get("_id", ""),
                "title": collection.get("title", ""),
                "count": collection.get("count", 0),
                "public": collection.get("public", False),
                "view": collection.get("view", ""),
                "color": collection.get("color", ""),
                "created": collection.get("created", ""),
                "lastUpdate": collection.get("lastUpdate", ""),
                "expanded": collection.get("expanded", False)
            }
            
            # Add parent ID if present
            if "parent" in collection and "$id" in collection["parent"]:
                result["parent_id"] = collection["parent"]["$id"]
            
            # Return native Python dict instead of JSON string
            return result
    except Exception as e:
        # Let exceptions bubble up to MCP
        raise ValueError(f"Error fetching collection: {str(e)}")

@mcp.tool("create_collection")
async def create_collection(
    title: str, 
    view: str = "list", 
    public: bool = False, 
    parent_id: Optional[int] = None
) -> str:
    """
    Create a new collection in Raindrop.io
    
    Args:
        title: Name of the collection
        view: View type (list, grid, masonry, simple)
        public: Whether the collection is public
        parent_id: ID of parent collection (omit for root collection)
    """
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        return json.dumps({
            "isError": True,
            "content": [{"type": "text", "text": "API token not set. Please check your .env file."}]
        })
        
    try:
        data = {
            "title": title,
            "view": view,
            "public": public
        }
        
        if parent_id is not None:
            data["parent"] = {"$id": parent_id}
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/collection",
                headers=headers,
                json=data
            )
            response_data = response.json()
            
            if not response_data.get("result", False):
                return json.dumps({
                    "isError": True,
                    "content": [{"type": "text", "text": f"Error creating collection: {response_data.get('errorMessage', 'Unknown error')}"}]
                })
            
            return json.dumps({
                "content": [
                    {"type": "text", "text": f"Collection '{title}' created successfully."},
                    {"type": "text", "text": f"Collection ID: {response_data.get('item', {}).get('_id', 'Unknown')}"}
                ]
            })
    except Exception as e:
        raise e  # Let exceptions bubble up
            
@mcp.tool("update_collection")
async def update_collection(
    collection_id: int, 
    title: Optional[str] = None,
    view: Optional[str] = None,
    public: Optional[bool] = None,
    parent_id: Optional[int] = None,
    expanded: Optional[bool] = None
) -> str:
    """
    Update an existing collection in Raindrop.io
    
    Args:
        collection_id: ID of the collection to update
        title: New name for the collection
        view: View type (list, grid, masonry, simple)
        public: Whether the collection is public
        parent_id: ID of parent collection (omit for root collection)
        expanded: Whether the collection is expanded
    """
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        return json.dumps({
            "isError": True,
            "content": [{"type": "text", "text": "API token not set. Please check your .env file."}]
        })
        
    try:
        data = {}
        if title is not None:
            data["title"] = title
        if view is not None:
            data["view"] = view
        if public is not None:
            data["public"] = public
        if parent_id is not None:
            data["parent"] = {"$id": parent_id}
        if expanded is not None:
            data["expanded"] = expanded
            
        if not data:
            return json.dumps({
                "isError": True,
                "content": [{"type": "text", "text": "No update parameters provided."}]
            })
            
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_URL}/collection/{collection_id}",
                headers=headers,
                json=data
            )
            response_data = response.json()
            
            if not response_data.get("result", False):
                return json.dumps({
                    "isError": True,
                    "content": [{"type": "text", "text": f"Error updating collection: {response_data.get('errorMessage', 'Unknown error')}"}]
                })
            
            return json.dumps({
                "content": [
                    {"type": "text", "text": f"Collection {collection_id} updated successfully."}
                ]
            })
    except Exception as e:
        raise e  # Let exceptions bubble up
    
@mcp.tool("delete_collection")
async def delete_collection(collection_id: int) -> str:
    """
    Delete a collection from Raindrop.io. The raindrops will be moved to Trash.
    
    Args:
        collection_id: ID of the collection to delete
    """
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        return json.dumps({
            "isError": True,
            "content": [{"type": "text", "text": "API token not set. Please check your .env file."}]
        })
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{API_URL}/collection/{collection_id}",
                headers=headers
            )
            response_data = response.json()
            
            if not response_data.get("result", False):
                return json.dumps({
                    "isError": True,
                    "content": [{"type": "text", "text": f"Error deleting collection: {response_data.get('errorMessage', 'Unknown error')}"}]
                })
            
            return json.dumps({
                "content": [
                    {"type": "text", "text": f"Collection {collection_id} deleted successfully."}
                ]
            })
    except Exception as e:
        raise e  # Let exceptions bubble up
            
@mcp.tool("empty_trash")
async def empty_trash() -> str:
    """
    Empty the trash in Raindrop.io, permanently deleting all raindrops in it.
    """
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        return json.dumps({
            "isError": True,
            "content": [{"type": "text", "text": "API token not set. Please check your .env file."}]
        })
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{API_URL}/collection/-99",
                headers=headers
            )
            response_data = response.json()
            
            if not response_data.get("result", False):
                return json.dumps({
                    "isError": True,
                    "content": [{"type": "text", "text": f"Error emptying trash: {response_data.get('errorMessage', 'Unknown error')}"}]
                })
            
            return json.dumps({
                "content": [
                    {"type": "text", "text": "Trash emptied successfully."}
                ]
            })
    except Exception as e:
        raise e  # Let exceptions bubble up

@mcp.tool("get_raindrop")
async def get_raindrop(raindrop_id: int) -> dict:
    """
    Get a single raindrop from Raindrop.io by ID
    
    Args:
        raindrop_id: ID of the raindrop to fetch
    """
    # Validate input
    if raindrop_id is None:
        raise ValueError("No raindrop ID provided")
    
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        raise ValueError("API token not set. Please check your .env file.")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/raindrop/{raindrop_id}", headers=headers)
            
            if response.status_code != 200:
                raise ValueError(f"API returned status {response.status_code}")
            
            data = response.json()
            
            if "item" not in data:
                raise ValueError("Unexpected API response format")
            
            # Return the raindrop item directly
            return data["item"]
    except Exception as e:
        # Let exceptions bubble up to MCP
        raise ValueError(f"Error fetching raindrop: {str(e)}")

@mcp.tool("get_raindrops")
async def get_raindrops(
    collection_id: int,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    page: Optional[int] = 0,
    perpage: Optional[int] = 25,
    nested: Optional[bool] = False
) -> dict:
    """
    Get multiple raindrops from a Raindrop.io collection
    
    Args:
        collection_id: ID of the collection to fetch raindrops from.
                       Use 0 for all raindrops, -1 for unsorted, -99 for trash.
        search: Optional search query
        sort: Sorting order. Options: -created (default), created, score, -sort, title, -title, domain, -domain
        page: Page number (starting from 0)
        perpage: Items per page (max 50)
        nested: Whether to include raindrops from nested collections
    """
    # Validate inputs
    if collection_id is None:
        raise ValueError("No collection ID provided")
    
    if perpage > 50:
        perpage = 50  # API limit
    
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        raise ValueError("API token not set. Please check your .env file.")
    
    try:
        # Build query parameters
        params = {}
        if search:
            params["search"] = search
        if sort:
            params["sort"] = sort
        if page is not None:
            params["page"] = page
        if perpage:
            params["perpage"] = perpage
        if nested:
            params["nested"] = "true"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/raindrops/{collection_id}", 
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise ValueError(f"API returned status {response.status_code}")
            
            return response.json()
    except Exception as e:
        # Let exceptions bubble up to MCP
        raise ValueError(f"Error fetching raindrops: {str(e)}")

@mcp.tool("get_tags")
async def get_tags(collection_id: Optional[int] = None) -> list:
    """
    Get tags from Raindrop.io
    
    Args:
        collection_id: Optional ID of the collection to fetch tags from.
                      When not specified, all tags from all collections will be retrieved.
    """
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        raise ValueError("API token not set. Please check your .env file.")
    
    try:
        # Build the endpoint URL
        endpoint = f"{API_URL}/tags"
        if collection_id is not None:
            endpoint = f"{endpoint}/{collection_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, headers=headers)
            
            if response.status_code != 200:
                raise ValueError(f"API returned status {response.status_code}")
            
            data = response.json()
            
            if not data.get("result", False) or "items" not in data:
                raise ValueError("Unexpected API response format")
            
            # Return just the tags array for simplicity
            return data["items"]
    except Exception as e:
        # Let exceptions bubble up to MCP
        raise ValueError(f"Error fetching tags: {str(e)}")

@mcp.tool("update_raindrop")
async def update_raindrop(
    raindrop_id: int,
    title: Optional[str] = None,
    excerpt: Optional[str] = None,
    link: Optional[str] = None,
    important: Optional[bool] = None,
    tags: Optional[List[str]] = None,
    collection_id: Optional[int] = None,
    cover: Optional[str] = None,
    type: Optional[str] = None,
    order: Optional[int] = None,
    pleaseParse: Optional[bool] = None
) -> dict:
    """
    Update an existing raindrop (bookmark) in Raindrop.io
    
    Args:
        raindrop_id: ID of the raindrop to update
        title: New title for the raindrop
        excerpt: New description/excerpt
        link: New URL
        important: Set to True to mark as favorite
        tags: List of tags to assign
        collection_id: ID of collection to move the raindrop to
        cover: URL for the cover image
        type: Type of the raindrop
        order: Sort order (ascending) - set to 0 to move to first place
        pleaseParse: Set to True to reparse metadata (cover, type) in the background
    """
    # Validate input
    if raindrop_id is None:
        raise ValueError("No raindrop ID provided")
    
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        raise ValueError("API token not set. Please check your .env file.")
    
    try:
        # Build the request body with only provided parameters
        data = {}
        if title is not None:
            data["title"] = title
        if excerpt is not None:
            data["excerpt"] = excerpt
        if link is not None:
            data["link"] = link
        if important is not None:
            data["important"] = important
        if tags is not None:
            data["tags"] = tags
        if collection_id is not None:
            data["collection"] = {"$id": collection_id}
        if cover is not None:
            data["cover"] = cover
        if type is not None:
            data["type"] = type
        if order is not None:
            data["order"] = order
        if pleaseParse:
            data["pleaseParse"] = {}
        
        if not data:
            raise ValueError("No update parameters provided")
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_URL}/raindrop/{raindrop_id}",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise ValueError(f"API returned status {response.status_code}")
            
            result = response.json()
            
            if not result.get("result", False):
                error_message = result.get("errorMessage", "Unknown error")
                raise ValueError(f"Error updating raindrop: {error_message}")
            
            return result
    except Exception as e:
        # Let exceptions bubble up to MCP
        raise ValueError(f"Error updating raindrop: {str(e)}")

@mcp.tool("update_many_raindrops")
async def update_many_raindrops(
    collection_id: int,
    ids: Optional[List[int]] = None,
    important: Optional[bool] = None,
    tags: Optional[List[str]] = None,
    cover: Optional[str] = None,
    target_collection_id: Optional[int] = None,
    nested: Optional[bool] = False,
    search: Optional[str] = None
) -> dict:
    """
    Update multiple raindrops at once within a collection
    
    Args:
        collection_id: ID of the collection containing raindrops to update
        ids: Optional list of specific raindrop IDs to update
        important: Set to True to mark as favorite, False to unmark
        tags: List of tags to add (or empty list to remove all tags)
        cover: URL for cover image (use '<screenshot>' to set screenshots for all)
        target_collection_id: ID of collection to move raindrops to
        nested: Include raindrops from nested collections
        search: Optional search query to filter which raindrops to update
    """
    # Validate input
    if collection_id is None:
        raise ValueError("No collection ID provided")
    
    headers = await get_headers()
    
    if not headers.get("Authorization"):
        raise ValueError("API token not set. Please check your .env file.")
    
    try:
        # Build the request body with only provided parameters
        data = {}
        if ids is not None:
            data["ids"] = ids
        if important is not None:
            data["important"] = important
        if tags is not None:
            data["tags"] = tags
        if cover is not None:
            data["cover"] = cover
        if target_collection_id is not None:
            data["collection"] = {"$id": target_collection_id}
        
        if not data:
            raise ValueError("No update parameters provided")
        
        # Build query params
        params = {}
        if search:
            params["search"] = search
        if nested:
            params["nested"] = "true"
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_URL}/raindrops/{collection_id}",
                headers=headers,
                json=data,
                params=params
            )
            
            if response.status_code != 200:
                raise ValueError(f"API returned status {response.status_code}")
            
            result = response.json()
            
            if not result.get("result", False):
                error_message = result.get("errorMessage", "Unknown error")
                raise ValueError(f"Error updating raindrops: {error_message}")
            
            return result
    except Exception as e:
        # Let exceptions bubble up to MCP
        raise ValueError(f"Error updating raindrops: {str(e)}")

if __name__ == "__main__":
    asyncio.run(mcp.run()) 