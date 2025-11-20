# Arka MCP Gateway

A centralized gateway for managing and connecting to multiple MCP (Model Context Protocol) servers. Provides secure, scalable access to MCP servers with SSO authentication, session isolation, and central management.

[![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/YVBgb8wh)
[![Website](https://img.shields.io/badge/Website-Visit%20Us-FF6B6B?style=for-the-badge&logo=google-chrome&logoColor=white)](https://www.arka.kenislabs.com)
[![GitHub](https://img.shields.io/badge/GitHub-Star%20Us-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/KenisLabs/arka-mcp-gateway)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)

> **📢 Community Edition** - This is the free, open-source version. For enterprise features like Azure AD SSO, Teams, AI Guardrails, Whitelabeling, and more, see [COMMERCIAL.md](./COMMERCIAL.md)

## Features (Community Edition)

- 🔐 **GitHub OAuth** - User authentication with GitHub
- 👤 **Admin Panel** - Create and manage users
- 🎯 **MCP Server Management** - Configure GitHub, Gmail, Slack, and more
- 🔑 **OAuth Provider Management** - Centralized OAuth credentials per server
- 🛠️ **Tool Management** - Enable/disable tools organization-wide
- 🔒 **Per-User Session Isolation** - Isolated user contexts per MCP server
- 👥 **User Dashboard** - Connect and authorize MCP servers
- 🚀 **Docker Compose Deployment** - Single command deployment
- 📚 **API Documentation** - Full OpenAPI/Swagger docs

## Enterprise Edition

Need more advanced features? Check out our [Enterprise Edition](./COMMERCIAL.md) which includes:

- ⭐ **Azure AD / SAML SSO** - Enterprise identity integration
- 👥 **Teams & Groups** - Organize users, team-based permissions
- 🛡️ **AI Guardrails** - Content filtering, PII detection, DLP
- 🎨 **Whitelabeling** - Custom branding, domain, remove Arka branding
- 📊 **Advanced Permissions** - Per-user/team tool overrides
- 📈 **Audit Logs** - Full compliance trail, SIEM integration
- 💰 **Cost Management** - Usage analytics, budget controls
- 🔒 **Enterprise Security** - CMEK, MFA, IP controls
- 🚀 **24/7 Support** - Priority support with SLA

[Learn more about Enterprise Edition →](./COMMERCIAL.md)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Domain name (for production) or localhost (for local development)

### 1. Clone Repository

```bash
git clone https://github.com/KenisLabs/arka-mcp-gateway.git
cd arka-mcp-gateway
```

### 2. Generate Secrets

```bash
# Generate JWT secret key (save this output)
openssl rand -hex 32

# Generate encryption key (save this output)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Configure Environment

Create `.env.production` file in the root directory:

```bash
# Database Configuration
POSTGRES_DB=arka_mcp_gateway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PORT=5432

# JWT Configuration (use output from openssl command)
ARKA_JWT_SECRET_KEY=<your_jwt_secret_here>
ARKA_JWT_ALGORITHM=HS256
ARKA_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ARKA_JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption (use output from python command)
ARKA_ENCRYPTION_KEY=<your_encryption_key_here>

# Application URLs
# For local development:
ARKA_FRONTEND_URL=http://localhost
ARKA_BACKEND_URL=http://localhost:8000
# For production:
# ARKA_FRONTEND_URL=https://your-domain.com
# ARKA_BACKEND_URL=https://your-domain.com

ARKA_WORKER_URL=http://worker:8001

# GitHub User OAuth (for user login)
# Create OAuth App at: https://github.com/settings/developers
# Callback URL: http://localhost:8000/auth/github/callback
ARKA_GITHUB_USER_OAUTH_CLIENT_ID=your_github_oauth_client_id
ARKA_GITHUB_USER_OAUTH_CLIENT_SECRET=your_github_oauth_client_secret

# Optional: Azure OAuth (for user login)
# ARKA_AZURE_CLIENT_ID=your_azure_client_id
# ARKA_AZURE_CLIENT_SECRET=your_azure_client_secret
# ARKA_AZURE_TENANT_ID=your_azure_tenant_id

# Ports
FRONTEND_PORT=80
BACKEND_PORT=8000
WORKER_PORT=8001
```

### 4. Start Application

```bash
docker-compose --env-file .env.production -f docker-compose.yml up -d
```

### 5. Bootstrap Admin User

```bash
# Create the initial admin user
curl -X POST http://localhost:8000/auth/admin/bootstrap

# Response will contain admin credentials - save them securely!
# Default: admin@example.com / <generated_password>
```

### 6. Access Application

- **Frontend**: http://localhost
- **Admin Login**: Use credentials from bootstrap step
- **API Docs**: http://localhost:8000/docs

## Architecture

```
┌─────────────┐
│   Nginx     │  ← Frontend (React + Vite)
│  (Port 80)  │
└──────┬──────┘
       │
       ├── /api/* ──────────────┐
       │                        ▼
       │              ┌──────────────┐      ┌──────────────┐
       │              │   Backend    │──────│  PostgreSQL  │
       │              │  (Port 8000) │      │  (Port 5432) │
       │              └──────┬───────┘      └──────────────┘
       │                     │
       │                     │
       └── /mcp ────────────┘
                             │
                             ▼
                   ┌──────────────┐
                   │    Worker    │  ← MCP Server Processes
                   │  (Port 8001) │
                   └──────┬───────┘
                          │
                ┌─────────┴────────┬──────────┬─────────┐
                ▼                  ▼          ▼         ▼
           GitHub MCP        Gmail MCP   Slack MCP    ...
```

## Configuration

### Setting Up OAuth for User Login

#### GitHub OAuth (Recommended)

1. Go to https://github.com/settings/developers
2. Create a New OAuth App
3. Set these values:
   - **Application name**: Arka MCP Gateway
   - **Homepage URL**: `http://localhost` (or your domain)
   - **Authorization callback URL**: `http://localhost:8000/auth/github/callback`
4. Copy Client ID and Client Secret to `.env.production`

#### Azure OAuth (Optional)

1. Go to Azure Portal → App Registrations
2. Create a new registration
3. Add redirect URI: `http://localhost:8000/auth/azure/callback`
4. Create a client secret
5. Copy values to `.env.production`

### Configuring MCP Server OAuth

After logging in as admin:

1. Navigate to **Admin Dashboard** → **MCP Server Management**
2. Click **Add MCP Server** or configure existing servers
3. Add OAuth credentials for each MCP server:
   - **GitHub MCP**: Requires GitHub OAuth App
   - **Gmail MCP**: Requires Google Cloud OAuth credentials
   - **Google Calendar MCP**: Requires Google Cloud OAuth credentials
   - **Slack MCP**: Requires Slack App credentials

### Adding New MCP Servers

1. Log in as admin
2. Go to **MCP Server Management**
3. Click **Browse Catalog** to see available servers
4. Select a server and configure OAuth credentials
5. Enable the server for your organization
6. Users can then authorize and connect to the server

## Local Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

### Database (Local Development)

```bash
docker run -d \
  --name arka-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=arka_mcp_gateway \
  -p 5432:5432 \
  postgres:16-alpine
```

## Troubleshooting

### Container Issues

```bash
# View logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Restart services
docker-compose restart backend

# Rebuild after code changes
docker-compose build frontend
docker-compose up -d
```

### Common Issues

**1. Database connection fails**

```bash
# Check if postgres is running
docker-compose ps

# Check database logs
docker-compose logs postgres
```

**2. OAuth callback errors**

- Verify callback URLs in OAuth provider settings match your `ARKA_BACKEND_URL`
- For GitHub: Should be `{BACKEND_URL}/auth/github/callback`
- For MCP servers: Should be `{BACKEND_URL}/servers/{server-id}/auth-callback`

**3. Admin bootstrap fails**

```bash
# Check if admin already exists in database
docker-compose exec postgres psql -U postgres -d arka_mcp_gateway -c "SELECT email, role FROM users WHERE role='admin';"

# If admin exists, you can reset password via database
```

**4. Frontend can't reach backend**

- Check nginx configuration in `frontend/nginx.conf`
- Verify backend container is running: `docker-compose ps backend`
- Check backend health: `curl http://localhost:8000/health`

## Tech Stack

### Backend

- **FastAPI** - Modern async Python web framework
- **PostgreSQL** - Primary database
- **SQLAlchemy** - Async ORM
- **JWT** - Token-based authentication
- **Cryptography** - Fernet encryption for OAuth secrets
- **Uvicorn** - ASGI server

### Frontend

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **React Router** - Client-side routing

### Infrastructure

- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy and static file serving

## Security

- **JWT Tokens**: HTTP-only cookies prevent XSS attacks
- **OAuth Credentials**: Encrypted at rest using Fernet (AES-128)
- **Password Hashing**: bcrypt for admin passwords
- **CORS**: Restricted to frontend URL
- **Rate Limiting**: Applied to authentication endpoints
- **HTTPS Ready**: Use SSL/TLS in production

## Project Structure

```
arka-mcp-gateway/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── auth/               # Authentication modules
│   ├── gateway/            # MCP gateway logic
│   ├── database.py         # Database configuration
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   └── lib/           # Utilities
│   ├── nginx.conf         # Nginx configuration
│   └── package.json       # Node dependencies
├── shared/                # Shared configuration
│   └── mcp_servers_catalog.json
├── docker-compose.yml     # Docker orchestration
├── .env.production        # Production environment variables
└── README.md             # This file
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/KenisLabs/arka-mcp-gateway/issues)
- **Discussions**: [GitHub Discussions](https://github.com/KenisLabs/arka-mcp-gateway/discussions)
- **Discord**: [Join our community](https://discord.gg/YVBgb8wh)
- **Enterprise Support**: [Schedule a call](https://calendly.com/ayushshivani12345/)
- **Email**: support@kenislabs.com

---

**Built with ❤️ by KenisLabs**
