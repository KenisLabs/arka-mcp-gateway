from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.github import router as github_router
from auth.admin import router as admin_router
from config import settings
from edition import is_enterprise_edition, get_enterprise_module
from gateway.servers import router as servers_router
from gateway.admin_endpoints import router as admin_endpoints_router
from gateway.tool_management_endpoints import router as tool_management_router
from gateway.mcp_server_endpoints import router as mcp_server_management_router
from gateway.mcp_token_endpoints import router as mcp_token_router
from database import init_db, close_db, get_db_session
from fastmcp import FastMCP
from arka_mcp.user_aware_server import authenticated_mcp_app
from gateway.tool_sync import sync_tools_on_startup
from middleware import EnterpriseRouteMiddleware

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI application.

    Handles startup and shutdown events:
    - Startup: Initialize database and create tables, initialize MCP test server
    - Shutdown: Close database connections
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Starting up Arka MCP Gateway...")

    # Check edition
    if is_enterprise_edition():
        logger.info("🏢 Edition: ENTERPRISE (Hosted by KenisLabs)")
    else:
        logger.info("🌟 Edition: COMMUNITY (Self-Hosted)")

    logger.info("=" * 60)

    try:
        await init_db()
        logger.info("Database initialized successfully")

        # Sync tools from filesystem to database
        async with get_db_session() as db:
            await sync_tools_on_startup(db)

        # Start authenticated MCP app lifespan by entering its context
        async with authenticated_mcp_app.router.lifespan_context(app):
            logger.info("Authenticated MCP server initialized")
            yield

    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Arka MCP Gateway...")
        await close_db()
        logger.info("Database connections closed")


app = FastAPI(
    title="Arka MCP Gateway",
    description="Enterprise MCP Gateway API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,  # Frontend URL
        "http://localhost:6274",  # MCP Inspector
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enterprise route interception middleware
# Must be added AFTER CORS but BEFORE route registration
# Intercepts enterprise routes in community edition and returns 402
app.add_middleware(EnterpriseRouteMiddleware)

# Include core routers (always available)
app.include_router(github_router)
app.include_router(admin_router)
app.include_router(admin_endpoints_router)
app.include_router(tool_management_router)
app.include_router(mcp_server_management_router)
app.include_router(mcp_token_router)
app.include_router(servers_router)

# Enterprise features (conditional registration)
# Enterprise routes are ONLY registered when enterprise submodule is present
# Community edition uses middleware to intercept and return 402
if is_enterprise_edition():
    logger.info("🔧 Loading enterprise features...")

    # Track which enterprise features successfully loaded
    loaded_features = []
    failed_features = []

    # Azure AD OAuth
    azure_module = get_enterprise_module("auth.azure")
    if azure_module and hasattr(azure_module, "router"):
        app.include_router(azure_module.router)
        loaded_features.append("Azure AD OAuth")
        logger.info("✅ Azure AD OAuth enabled")
    else:
        failed_features.append("Azure AD OAuth")
        logger.warning("⚠️  Azure AD module not available - skipping")

    # Per-user tool permissions
    try:
        from enterprise.tool_permissions import router as enterprise_tool_permissions_router
        app.include_router(enterprise_tool_permissions_router)
        loaded_features.append("Per-User Tool Permissions")
        logger.info("✅ Per-User Tool Permissions enabled")
    except ImportError:
        failed_features.append("Per-User Tool Permissions")
        logger.warning("⚠️  Enterprise tool permissions module not available - skipping")

    # Log summary
    if loaded_features:
        logger.info(f"✅ Enterprise features loaded: {', '.join(loaded_features)}")
    if failed_features:
        logger.warning(
            f"⚠️  Enterprise features unavailable: {', '.join(failed_features)}"
        )
        logger.info(
            "ℹ️  Application will continue with available features"
        )
else:
    # Community edition
    logger.info("ℹ️  Running Community Edition")
    logger.info("ℹ️  Enterprise features will return 402 Payment Required")


@app.get("/")
async def root():
    """Root endpoint with edition information"""
    return {
        "name": "Arka MCP Gateway",
        "version": "0.1.0",
        "status": "running",
        "edition": "enterprise" if is_enterprise_edition() else "community",
        "hosted_by": "kenislabs" if is_enterprise_edition() else "self-hosted",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Mount authenticated MCP server at root
# Note: FastMCP internally creates routes like /mcp/messages, /mcp/sse, etc.
# Mounting at "/" allows FastMCP to handle its own path structure
# IMPORTANT: This must be the LAST mount to avoid intercepting REST API routes
app.mount("/", authenticated_mcp_app)
logger.info("Mounted MCP server at / (FastMCP handles /mcp/* internally)")

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
