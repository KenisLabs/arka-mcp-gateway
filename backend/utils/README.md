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

## OAuth Provider Testing

### Manual Testing Steps for New OAuth Providers

After implementing a new OAuth provider (e.g., Notion), follow these steps to verify:

#### 1. Backend Startup Test

```bash
# Start backend service
docker-compose up backend

# Check logs for successful provider initialization
# Expected log messages:
# - "Notion OAuth provider initialized from environment variables" (if env vars set)
# - OR "Notion OAuth credentials not found in environment. Will check database when provider is requested."
# - No import errors
# - Backend starts successfully on port 8000
```

#### 2. Admin Configuration Test

Access admin dashboard at `http://localhost:3000/admin/mcp-servers`:

- Verify Notion appears in MCP Server configuration list
- Configure OAuth credentials (Client ID, Client Secret, Redirect URI)
- For Notion: Leave scopes empty (doesn't use OAuth scopes)
- Save configuration
- Expected: Success message, credentials stored encrypted

#### 3. User Authorization Flow Test

As a regular user:

1. Navigate to `http://localhost:3000/mcp-servers`
2. Find Notion in server list
3. Click "Connect" or "Authorize"
4. Should redirect to Notion authorization page
5. Select workspace and authorize
6. Redirect back to callback URL
7. Token exchange completes
8. User sees "Connected" status

#### 4. Security Verification Checklist

- [ ] Client secrets encrypted in database
- [ ] No secrets in logs (only first 8 chars shown)
- [ ] Error messages sanitized (no internal details)
- [ ] CSRF protection via state parameter
- [ ] Redirect URI validation
- [ ] Rate limiting respected

### Notion OAuth Provider - PR#1 Status

**Files Changed:**
- ✅ `backend/gateway/auth_providers/notion.py` (new, ~400 LOC)
- ✅ `backend/gateway/auth_providers/registry.py` (modified)

**Code Verification:**
- ✅ Python syntax valid
- ✅ AST structure correct
- ✅ Import in registry.py
- ✅ Environment initialization
- ✅ Database initialization
- ✅ server_to_provider_name mapping exists
- ✅ Follows Gmail/GCal/Slack pattern

**Notion-Specific OAuth:**
- Uses Basic auth for token exchange (not Bearer)
- Tokens are permanent (no expiration/refresh)
- Workspace-based authorization
- No programmatic revocation
- Requires Notion-Version header on API requests

**Next Steps:** PR#2 (API Client), PR#3 (Models), PR#4-8 (Tool Implementation)

See `localDocs/NOTION_PR_BREAKDOWN.md` for full implementation plan.

## Notes

- All scripts should be run from the `backend/` directory using Python module syntax (`python -m utils.<script_name>`)
- Scripts use async/await and require the same database setup as the main application
- Make sure the database is accessible before running these scripts
