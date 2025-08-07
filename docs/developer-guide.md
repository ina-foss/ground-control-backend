# INA Ground Control API Developer Guide

### Prerequisites

- Python 3.10 or higher
- [UV package manager](https://docs.astral.sh/uv/) (installed and configured for this project)
- PostgreSQL database server
- Git for version control

### Initial Setup

```shell script
# Clone the repository
git clone <repository-url>
cd backend

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

This project uses **uv** as the primary package manager. Key commands:

```shell script
# Install dependencies
uv sync

# Install with development dependencies
uv sync --group dev

# Example:  Add a new dependency
uv add requests

# Add a development dependency
uv add --group dev pytest

# Update dependencies
uv lock --upgrade
```

### Installation

Install dependencies including development tools:

```bash
uv sync
```

This will install all project dependencies plus development tools like pytest, black, isort, and pylint.

### Environment Setup

Copy the example environment file and configure your local settings:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your database credentials and other configuration values. See
the [Configuration section in README.md](../README.md#configuration) for available options.

### Docker Services

Start the development stack:

```bash
  docker compose -f .dev/services.yml up -d
```

Stop the development stack:

```bash
  docker compose -f .dev/services.yml down
```

### Running the Application

Start the development server:

```bash
# Apply database migrations
uv run alembic upgrade head

# Start the development server with hot reload
uv run uvicorn ina_ground_control.main:app --reload --host 0.0.0.0 --port 8000
```

**Note:** If you're behind a proxy or facing connection issues, try running:

```bash
HTTP_PROXY='' HTTPS_PROXY='' http_proxy='' https_proxy='' \
uv run uvicorn ina_ground_control.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- **API**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### Testing

Run the complete test suite:

```bash
uv run pytest
```

Run tests with coverage report:

```bash
uv run pytest --cov=ina_ground_control --cov-report=html --cov-report=term-missing
```

Run specific test categories:

```bash
# Unit tests only
uv run pytest -m unit
```

Coverage reports will be generated in `htmlcov/` directory.

### Code Quality & Linting

Format code with Black:

```bash
uv run black .
```

Sort imports with isort:

```bash
uv run isort .
```

Check code style with Pylint:

```bash
uv run pylint ina_ground_control
```

Run all quality checks at once:

```bash
uv run black . && uv run isort . && uv run pylint ina_ground_control
```

### Database Management

Generate new migration after model changes:

```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

Apply migrations to database:

```bash
uv run alembic upgrade head
```
