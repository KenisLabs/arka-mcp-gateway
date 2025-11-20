# Backend Utility Scripts

This directory contains utility scripts for development and database maintenance.

## Scripts

### populate_tools.py

**Purpose:** Syncs the tool database with the filesystem by discovering tools from `arka_mcp/servers/*_tools/` directories.

**Usage:**

```bash
# Apply changes to database
cd backend
python -m utils.populate_tools

# Preview changes without applying (dry run)
python -m utils.populate_tools --dry-run
```

**When to run:**

- After adding new MCP servers
- After adding/removing/renaming tools
- To sync database with codebase

### reset_tools.py

**Purpose:** Completely resets the tool database by deleting all tools and repopulating from filesystem.

**Usage:**

```bash
cd backend
python -m utils.reset_tools
```

**When to run:**

- When tool data is corrupted or stale
- After major changes to tool structure

### check_tools.py

**Purpose:** Displays all tools in the database with their status and permissions.

**Usage:**

```bash
cd backend
python -m utils.check_tools
```

**When to run:**

- To verify tool database contents
- To check organization permissions

### clear_mcp_tokens.py

**Purpose:** Deletes all MCP access tokens from the database (for testing).

**Usage:**

```bash
cd backend
python -m utils.clear_mcp_tokens
```

**When to run:**

- During development/testing
- To clear all OAuth tokens

## Notes

- All scripts should be run from the `backend/` directory using Python module syntax (`python -m utils.<script_name>`)
- Scripts use async/await and require the same database setup as the main application
- Make sure the database is accessible before running these scripts
