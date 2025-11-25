# Backend Utility Scripts

This directory contains utility scripts for development and database maintenance.

## Automatic Tool Synchronization

**IMPORTANT:** Tool synchronization now happens **automatically on backend startup** via `gateway/tool_sync.py`. The system will:
- ✅ Create new tools found in filesystem
- ✅ Update metadata for existing tools
- ✅ **Delete orphaned tools** (tools in DB but removed from filesystem)
- ✅ Clean up associated permissions

You'll see logs like:
```
🔄 Synchronizing tools from filesystem to database...
✓ Tool sync complete: 5 created, 2 updated, 1 deleted across 3 servers
```

**This means:** When you delete a tool file, it will be automatically removed from the database on the next backend restart.

## Scripts

### populate_tools.py

**Purpose:** Manually sync the tool database with the filesystem.

**Note:** This script is now **optional** since automatic sync runs on startup. However, it's still useful for:
- Testing tool discovery logic without restarting backend
- Previewing changes with `--dry-run` before committing
- Manual database verification
- Development and debugging

**Usage:**

```bash
# Apply changes to database
cd backend
python -m utils.populate_tools

# Preview changes without applying (dry run)
python -m utils.populate_tools --dry-run
```

**When to run:**

- Testing tool changes without restarting backend
- Verifying tool metadata is correct
- Debugging tool discovery issues
- Development/testing workflows

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
