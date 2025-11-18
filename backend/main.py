from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.github import router as github_router
from auth.admin import router as admin_router
from config import settings
from gateway.servers import router as servers_router
from gateway.admin_endpoints import router as admin_endpoints_router
from gateway.tool_management_endpoints import router as tool_management_router
from gateway.mcp_server_endpoints import router as mcp_server_management_router
from gateway.mcp_token_endpoints import router as mcp_token_router
from database import init_db, close_db, get_db_session
from fastmcp import FastMCP
from arka_mcp.user_aware_server import authenticated_mcp_app
from gateway.tool_sync import sync_tools_on_startup

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
    logger.info("Starting up Arka MCP Gateway...")
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

# Include routers
app.include_router(github_router)
app.include_router(admin_router)
app.include_router(admin_endpoints_router)
app.include_router(tool_management_router)
app.include_router(mcp_server_management_router)
app.include_router(mcp_token_router)
app.include_router(servers_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"name": "Arka MCP Gateway", "version": "0.1.0", "status": "running"}


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
