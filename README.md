# Raindrop MCP Server

This is a Model Context Protocol (MCP) server for Raindrop.io powered by the [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk/tree/main). It provides an easy way to read and update your bookmarks from the Raindrop personal knowledge management system from Claude Desktop in simple, human language. This can be paired with the [Firecrawl MCP server](https://github.com/mendableai/firecrawl-mcp-server#) to read the URLs associated with your bookmarks and classify them accordingly.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- [Claude Desktop](https://claude.ai/desktop)
- A Raindrop.io account and API token

## Setup

### 1. Obtain a Raindrop API Token

1. Go to [Raindrop.io Developer Portal](https://app.raindrop.io/settings/integrations)
2. Create a new app
3. Copy your API token

### 2. Set Your API Token

Set your Raindrop API token as an environment variable:

1. Create a .env file in the root directory
2. Add new line: ```RAINDROP_TOKEN="your_token_here"```


## Development

To run the server in development mode:

```
uv run mcp dev server.py
```

## Installation

To install the server to Claude Desktop:

```
uv run mcp install server.py
```

This will start the server locally and allow you to test changes.

## Features

The server provides:

- Access to your Raindrop collections and raindrop data through capabilities
- Support for viewing root collections, child collections, or a specific collection by ID
- Tools to create, update, and delete collections and raindrops
- Tools to create and update new tags

## Example Queries

After installing the server to Claude Desktop, you can ask Claude questions and commands like:

- "Show me all my Raindrop collections"
- "Do I have any collections related to programming?"
- "Add this tag to all raindrops in this collection"
- "Show me the details of my Raindrop collection with ID 12345"
- "What child collections do I have in Raindrop?"
- "Create a new Raindrop collection called 'Claude Resources'"

Here is some example usage in Claude Desktop (paired with a Firecrawl MCP server):

Input to Claude Desktop as the classificaiton system:
![classifier](https://github.com/user-attachments/assets/648d587f-6e10-42b3-b759-878110ce1d66)

Output from Claude Desktop:
![classifier-output](https://github.com/user-attachments/assets/60d67757-cda5-472b-895d-c31b1fdd3631)


## Tools

The server provides the following MCP tools that let Claude Desktop perform actions on your Raindrop collections:

### create_collection

Creates a new collection in Raindrop.io.

**Parameters:**
- `title` (required): Name of the collection
- `view`: View type (list, grid, masonry, simple)
- `public`: Whether the collection is public
- `parent_id`: ID of parent collection (omit for root collection)

### update_collection

Updates an existing collection in Raindrop.io.

**Parameters:**
- `collection_id` (required): ID of the collection to update
- `title`: New name for the collection
- `view`: View type (list, grid, masonry, simple)
- `public`: Whether the collection is public
- `parent_id`: ID of parent collection (omit for root collection)
- `expanded`: Whether the collection is expanded

### delete_collection

Deletes a collection from Raindrop.io. The raindrops will be moved to Trash.

**Parameters:**
- `collection_id` (required): ID of the collection to delete

### empty_trash

Empties the trash in Raindrop.io, permanently deleting all raindrops in it.

### get_raindrop

Gets a single raindrop from Raindrop.io by ID.

**Parameters:**
- `raindrop_id` (required): ID of the raindrop to fetch

### get_raindrops

Gets multiple raindrops from a Raindrop.io collection.

**Parameters:**
- `collection_id` (required): ID of the collection to fetch raindrops from. Use 0 for all raindrops, -1 for unsorted, -99 for trash.
- `search`: Optional search query
- `sort`: Sorting order (options: -created, created, score, -sort, title, -title, domain, -domain)
- `page`: Page number (starting from 0)
- `perpage`: Items per page (max 50)
- `nested`: Whether to include raindrops from nested collections

### get_tags

Gets tags from Raindrop.io.

**Parameters:**
- `collection_id`: Optional ID of the collection to fetch tags from. When not specified, all tags from all collections will be retrieved.

### update_raindrop

Updates an existing raindrop (bookmark) in Raindrop.io.

**Parameters:**
- `raindrop_id` (required): ID of the raindrop to update
- `title`: New title for the raindrop
- `excerpt`: New description/excerpt
- `link`: New URL
- `important`: Set to True to mark as favorite
- `tags`: List of tags to assign
- `collection_id`: ID of collection to move the raindrop to
- `cover`: URL for the cover image
- `type`: Type of the raindrop
- `order`: Sort order (ascending) - set to 0 to move to first place
- `pleaseParse`: Set to True to reparse metadata (cover, type) in the background

### update_many_raindrops

Updates multiple raindrops at once within a collection.

**Parameters:**
- `collection_id` (required): ID of the collection containing raindrops to update
- `ids`: Optional list of specific raindrop IDs to update
- `important`: Set to True to mark as favorite, False to unmark
- `tags`: List of tags to add (or empty list to remove all tags)
- `cover`: URL for cover image (use '<screenshot>' to set screenshots for all)
- `target_collection_id`: ID of collection to move raindrops to
- `nested`: Include raindrops from nested collections
- `search`: Optional search query to filter which raindrops to update

  
## Dependencies

Please see `pyproject.toml` for dependancies.

These will be installed automatically when using `uv run mcp install` or `uv run mcp dev`.

## Contributing

Contributions are welcome! Here's how you can contribute to this project:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Validate they work as intended
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Open a pull request

Please ensure your code follows the existing style and includes appropriate documentation.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

