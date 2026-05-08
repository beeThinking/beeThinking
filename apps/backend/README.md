# 🐝 BeeThinking Backend

Modern REST API backend for BeeThinking built with FastAPI, SQLAlchemy, and JWT authentication. Optimized for Raspberry Pi deployment.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Features

- ✅ **REST API** with FastAPI (async/await support)
- ✅ **User Authentication** - Registration & JWT-based login
- ✅ **Password Security** - Bcrypt hashing with salt
- ✅ **Database Adapter Pattern** - Easy switching between SQLite and PostgreSQL
- ✅ **Environment Variables** - Secure configuration management
- ✅ **Docker Support** - Containerized deployment ready
- ✅ **CORS Enabled** - Frontend integration ready
- ✅ **Auto Documentation** - Swagger UI & ReDoc
- ✅ **Raspberry Pi Optimized** - Resource-efficient design

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Database Setup](#-database-setup)
- [Docker Deployment](#-docker-deployment)
- [Frontend Integration](#-frontend-integration)
- [Security](#-security)
- [Development](#-development)
- [Raspberry Pi Deployment](#-raspberry-pi-deployment)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

### Option 1: Quick Start Script (Recommended)

```bash
cd apps/backend
./start.sh
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment variables
cp .env.example .env
# Edit .env and set your SECRET_KEY

# 4. Start server
uvicorn app.main:app --reload
```

### Access the API

- **API Root**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Project Structure

```
BeeThinking/
├── app/
│   ├── api/                    # API Endpoints
│   │   ├── auth.py            # Registration & Login
│   │   ├── users.py           # User Management
│   │   └── dependencies.py    # JWT Authentication
│   ├── core/                   # Core Functionality
│   │   ├── config.py          # Environment Configuration
│   │   └── security.py        # Password Hashing & JWT
│   ├── crud/                   # Database Operations
│   │   └── user.py            # User CRUD
│   ├── db/                     # Database Setup
│   │   └── database.py        # SQLAlchemy Config
│   ├── models/                 # Database Models
│   │   └── user.py            # User Model
│   ├── schemas/                # Pydantic Schemas
│   │   └── user.py            # API Schemas
│   └── main.py                 # FastAPI Application
├── tests/                      # Test Suite (73 tests)
│   ├── unit/                  # Unit Tests
│   │   ├── test_api/          # API endpoint tests
│   │   ├── test_core/         # Security tests
│   │   └── test_crud/         # Database tests
│   ├── integration/           # Integration tests
│   ├── conftest.py            # Shared test fixtures
│   └── README.md              # Test documentation
├── .env                        # Environment Variables (create from .env.example)
├── .env.example                # Example Configuration
├── requirements.txt            # Python Dependencies
├── pytest.ini                  # Pytest Configuration
├── Dockerfile                  # Docker Image
├── docker-compose.yml          # Docker Compose Setup
├── start.sh                    # Development Start Script
└── README.md                   # This File
```

## 🔌 API Endpoints

### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint with API info |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/docs` | Swagger UI documentation |
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login and get JWT token |

### Protected Endpoints (JWT Token Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/me` | Get current user info |

### Request Examples

**Register User:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePass123"
```

**Get Current User:**
```bash
curl http://localhost:8000/api/users/me \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

## 🗄️ Database Setup

### SQLite (Development - Default)

Perfect for development and testing. No installation required!

```env
DATABASE_URL=sqlite:///./beethinking.db
```

✅ Already configured and works out of the box

### PostgreSQL (Production - Recommended for Raspberry Pi)

#### Option 1: With Docker

```bash
# Update .env
DATABASE_URL=postgresql://beethinking:beethinking@db:5432/beethinking

# Start with Docker Compose
docker-compose up -d
```

#### Option 2: Native Installation (Raspberry Pi)

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib python3-dev libpq-dev

# Create database and user
sudo -u postgres createuser beethinking
sudo -u postgres createdb beethinking
sudo -u postgres psql -c "ALTER USER beethinking WITH PASSWORD 'your_password';"

# Update .env
DATABASE_URL=postgresql://beethinking:your_password@localhost:5432/beethinking

# Install Python PostgreSQL adapter
pip install psycopg2-binary

# Restart server
```

## 🐋 Docker Deployment

### Build and Run with Docker Compose

Run from the **repository root**:

```bash
# Build and start all services (DB + Backend + Frontend)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Docker Compose Configuration

The root `docker-compose.yml` includes:
- **Frontend**: Angular app served via Nginx
- **Backend**: FastAPI application
- **PostgreSQL**: Database service
- **Health checks**: Automatic monitoring
- **Volumes**: Persistent data storage
- **Network**: Isolated network for services

## 💻 Frontend Integration

### API Base URL

```javascript
const API_BASE_URL = "http://localhost:8000/api";
```

### Example: User Registration (JavaScript/React)

```javascript
const register = async (username, email, password) => {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  });
  
  if (!response.ok) {
    throw new Error('Registration failed');
  }
  
  return await response.json();
};
```

### Example: User Login

```javascript
const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData
  });
  
  if (!response.ok) {
    throw new Error('Login failed');
  }
  
  const { access_token } = await response.json();
  localStorage.setItem('token', access_token);
  return access_token;
};
```

### Example: Authenticated Request

```javascript
const getCurrentUser = async () => {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get user data');
  }
  
  return await response.json();
};
```

## 🔐 Security

### Implemented Security Features

- ✅ **Bcrypt Password Hashing** - Passwords are hashed with salt
- ✅ **JWT Token Authentication** - Secure token-based sessions
- ✅ **Token Expiration** - 30-minute expiry (configurable)
- ✅ **Environment Variables** - Secrets not in code
- ✅ **CORS Configuration** - Controlled access from frontend
- ✅ **Password Validation** - Minimum 8 characters

### Generate New SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and update your `.env` file:

```env
SECRET_KEY=your_generated_secret_key_here
```

### Production Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Set `DEBUG=False` in production
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS (Let's Encrypt)
- [ ] Implement rate limiting
- [ ] Set up monitoring and logging
- [ ] Regular security updates
- [ ] Database backups

## 🛠️ Development

### Prerequisites

- Python 3.11+ (tested with 3.14)
- pip
- Optional: Docker & Docker Compose

### Install Development Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Key environment variables:

```env
# Database
DATABASE_URL=sqlite:///./beethinking.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=BeeThinking Backend
DEBUG=True

# CORS
FRONTEND_URL=http://localhost:3000

# Email (Optional)
EMAIL_CONFIRMATION_ENABLED=False
```

### Running in Development Mode

```bash
# With auto-reload
uvicorn app.main:app --reload

# Custom host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🥧 Raspberry Pi Deployment

### Why Raspberry Pi?

- Cost-effective 24/7 server
- Low power consumption
- ARM architecture support
- Perfect for small to medium projects

### Recommended Database for Raspberry Pi

**PostgreSQL** is recommended for production because:
- Better performance with concurrent users
- ACID compliance
- Better data integrity
- Scalable

**SQLite** can be used for:
- Single-user applications
- Low traffic scenarios
- Quick prototypes

### Docker on Raspberry Pi

**Is Docker worth it?**

✅ **Yes, Docker is recommended for Raspberry Pi because:**
- Consistent environment across devices
- Easy updates and rollbacks
- Isolated from system dependencies
- Simple backup and migration
- Resource limits can be set

### Raspberry Pi Deployment Steps

```bash
# 1. Clone repository on Raspberry Pi
git clone <your-repository-url>
cd beeThinking

# 2. Copy and edit environment file
cp apps/backend/.env.example apps/backend/.env
nano apps/backend/.env  # Update SECRET_KEY and DATABASE_URL

# 3. Install Docker (if not installed)
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 4. Start with Docker Compose
docker-compose up -d

# 5. Check logs
docker-compose logs -f backend

# 6. Access API
# http://<raspberry-pi-ip>:8000
```

### Resource Optimization for Raspberry Pi

In `docker-compose.yml`, you can set resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

## 🧪 Testing

### Test Suite

The project includes a comprehensive test suite with **73 tests** covering:
- Unit Tests (61 tests) - Fast, isolated component tests
- Integration Tests (12 tests) - End-to-end API flow tests

```
tests/
├── unit/                    # Unit Tests
│   ├── test_api/           # API endpoint tests
│   ├── test_core/          # Security & core functionality
│   └── test_crud/          # Database operations
└── integration/            # Integration/E2E tests
```

### Running Tests

**Install test dependencies:**
```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

**Run all tests:**
```bash
pytest
```

**Run only unit tests (fast):**
```bash
pytest -m unit
```

**Run only integration tests:**
```bash
pytest -m integration
```

**Run with coverage report:**
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

**Run specific test file:**
```bash
pytest tests/unit/test_core/test_security.py -v
```

### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| Security (bcrypt, JWT) | 17 | ✅ 100% |
| User CRUD | 15 | ✅ 100% |
| Auth API | 18 | ✅ 100% |
| Users API | 20 | ✅ 100% |
| Integration/E2E | 12 | ✅ 100% |

### Test Documentation

For detailed test documentation, see [`tests/README.md`](tests/README.md)

### Manual Testing with Swagger UI

1. Open http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Enter test data
5. Click "Execute"

### Testing with curl

See [API Endpoints](#-api-endpoints) section for curl examples.

## 🆘 Troubleshooting

### Server Won't Start

```bash
# Check if port 8000 is already in use
lsof -ti:8000 | xargs kill -9

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python version
python --version  # Should be 3.11+
```

### Database Errors

```bash
# For SQLite, delete and recreate database
rm beethinking.db
# Restart server

# For PostgreSQL, check connection
psql -U beethinking -d beethinking -h localhost
```

### Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Docker Issues

```bash
# Restart containers
docker-compose restart

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **FastAPI**: https://fastapi.tiangolo.com
- **SQLAlchemy**: https://docs.sqlalchemy.org
- **Pydantic**: https://docs.pydantic.dev

## 📦 Dependencies

Main dependencies (see `requirements.txt` for full list):

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **Passlib** - Password hashing
- **python-jose** - JWT tokens
- **python-multipart** - Form data parsing
- **email-validator** - Email validation

## 🗺️ Roadmap

### Current Features ✅

- User registration and authentication
- JWT token-based sessions
- Password hashing with Bcrypt
- SQLite and PostgreSQL support
- Docker deployment
- API documentation
- CORS configuration

### Planned Features 🔮

- [ ] Email verification (infrastructure ready)
- [ ] Password reset functionality
- [ ] User profile updates
- [ ] Refresh tokens
- [ ] Admin panel
- [ ] Role-based permissions
- [ ] Rate limiting
- [ ] Logging and monitoring
- [ ] CI/CD pipeline
- [ ] Unit and integration tests

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Support

If you have any questions or run into issues, please:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the [Documentation](#-documentation)
3. Open an issue on GitHub

## 👨‍💻 Developer

Developed with ☕ and 🐝 for the BeeThinking project.

---

**Happy coding! 🐝✨**

