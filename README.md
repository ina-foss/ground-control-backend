# Ground Control

Ground Control is an audio/video corpus annotation application developed by [INA](http://www.ina.fr) and distributed under an MIT license.
It is partially funded by BPI as part of the France 2030 [ArGiMi project](https://www.ina.fr/institut-national-audiovisuel/research/argimi-project).

Ground Control allows users to manage corpora, annotators, and task allocation strategies for annotators. There are several types of tasks, each with a dedicated screen. One of the main objectives of this application is to annotate audio transcripts while having synchronized access to the relevant media. The first screen currently in operation allows transcripts to be segmented and categorized. Others are under development, notably for the creation and fine annotation of spans within transcripts.

The application consists of a backend API, this project, and a frontend [available here](https://github.com/ina-foss/ground-control-frontend). The [amalia.js video player](https://ina-foss.github.io/amalia.js/) is integrated.


# Ground Control API

A secure FastAPI-based backend system designed for ground truth data management and secure client-server communication.

## Description

Ground Control API provides a robust backend infrastructure for managing ground truth data in machine learning workflows.
The system implements enterprise-grade security through SSO integration, comprehensive CORS policies, and structured configuration management.
It features automated database migrations, testing coverage, and production-ready monitoring with OpenTelemetry integration.

## Key Technologies & Techniques

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, high-performance web framework with automatic API documentation
- **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** - Type-safe configuration management using environment variables
- **[SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)** - Modern async-capable ORM with declarative mappings
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database migration management with PostgreSQL enum support
- **[FastAPI Keycloak Middleware](https://github.com/fastapi-keycloak/fastapi-keycloak)** - Production SSO authentication integration
- **[OpenTelemetry](https://opentelemetry.io/)** - Distributed tracing and metrics collection with Prometheus export
- **[UV Package Manager](https://docs.astral.sh/uv/)** - Fast Python package management and dependency resolution
- **[Environment-based Configuration](https://pydantic-docs.helpmanual.io/usage/settings/)** - Multi-environment settings with `.env` file support

## Notable Libraries & Dependencies

- **[psycopg2-binary](https://pypi.org/project/psycopg2-binary/)** - PostgreSQL database adapter
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** - Environment variable loading from `.env` files
- **[jsonpath-ng](https://pypi.org/project/jsonpath-ng/)** - JSONPath implementation for data extraction
- **[alembic-postgresql-enum](https://pypi.org/project/alembic-postgresql-enum/)** - Enhanced PostgreSQL enum support for migrations
- **[opentelemetry-exporter-prometheus](https://pypi.org/project/opentelemetry-exporter-prometheus/)** - Metrics export to Prometheus monitoring
- **[pytest-asyncio](https://pytest-asyncio.readthedocs.io/)** - Async testing support for FastAPI endpoints

## Project Structure

```
├── .dev/                       # Development environment configuration
├── docs/                       # Documentation source
├── tests/                      # Test suite (unit and integration)
├── static/                     # Static file serving directory
├── ina_ground_control/         # Main application package
│   ├── auth/                   # Authentication and authorization
│   ├── config/                 # Configuration modules
│   ├── models/                 # SQLAlchemy database models  
│   ├── routers/                # FastAPI route definitions
│   ├── schemas/                # Pydantic data validation schemas
│   ├── services/               # Business logic layer
│   ├── utils/                  # Utility functions and helpers
│   ├── constants/              # Application constants
│   ├── exception/              # Custom exception handlers
│   └── alembic/                # Database migration scripts
├── pyproject.toml              # Project configuration and dependencies
├── alembic.ini                 # Alembic migration configuration
├── logging.conf                # Application logging configuration
└── settings.py                 # Centralized settings management
```

**Key Directories:**
- **`.dev/`** - Contains Docker Compose configurations and development tooling setup
- **`ina_ground_control/auth/`** - Implements Keycloak SSO integration and JWT token handling
- **`ina_ground_control/models/`** - Database schema definitions with SQLAlchemy 2.0 declarative style
- **`ina_ground_control/alembic/`** - Database versioning and migration management

## Configuration

The application uses environment-based configuration through the [`settings.py`](settings.py) file, which leverages Pydantic Settings for type-safe configuration management. All settings can be overridden using environment variables with the `GC_` prefix.

### Available Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `GC_APPLICATION` | "Ground Control API" | Application name |
| `GC_VERSION` | "1.0.0" | Application version |
| `GC_SERVER_HOST` | "0.0.0.0" | Server bind address |
| `GC_SERVER_PORT` | 8000 | Server port |
| `GC_SSL_CERT_FILE` | "" | SSL certificate file path |
| `GC_API_DOCS_PATH` | "/docs" | OpenAPI documentation endpoint |
| `GC_LOG_LEVEL` | "info" | Logging level (debug, info, warning, error) |
| `GC_DEBUG` | false | Enable debug mode |

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GC_DB_SERVER` | "postgresql+psycopg2" | Database server type |
| `GC_DB_HOSTNAME` | "localhost" | Database host |
| `GC_DB_DATABASE` | "ground_control_db" | Database name |
| `GC_DB_USERNAME` | "postgres" | Database username |
| `GC_DB_PASSWORD` | "" | Database password |
| `GC_DB_PORT` | 5432 | Database port |

### SSO Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GC_SSO_URL` | "http://localhost:9080" | Keycloak server URL |
| `GC_SSO_REALM` | "ground_control" | Keycloak realm name |
| `GC_SSO_CLIENT_ID` | "internal" | OAuth2 client identifier |
| `GC_SSO_CLIENT_SECRET` | "internal" | OAuth2 client secret |

### Plugin Secret Encryption

Plugin `client_secret` values are encrypted at rest using Fernet (AES-128-CBC + HMAC-SHA256).

| Variable | Default | Description |
|----------|---------|-------------|
| `GC_SECRET_ENCRYPTION_KEY` | `""` | Fernet key used to encrypt plugin client secrets in the database |

Generate a key and add it to `.env.local`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Add to .env.local:
# GC_SECRET_ENCRYPTION_KEY=<generated-key>
```

> Secrets already stored in plaintext (without the `fernet:` prefix) are read as-is — no migration required.

### Environment Files

Configuration is loaded from multiple environment files in order of precedence:
1. `.env.prod` - Production environment settings
2. `.env.local` - Local development overrides
3. `.env` - Base environment configuration

Use the provided [`.env.local.example`](.env.local.example) as a template for local development setup.
