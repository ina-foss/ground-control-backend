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
  docker compose -f .dev/app.yml up -d
```

Stop the development stack:

```bash
  docker compose -f .dev/app.yml down
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

---

## Plugin Secret Encryption

Plugin `client_secret` values (OAuth2 credentials stored in the database) are encrypted at rest using **Fernet** symmetric encryption (AES-128-CBC + HMAC-SHA256) from the `cryptography` package.

### How it works

| Step | Where | What happens |
|---|---|---|
| **Save** | `plugin_service.create_plugin_crud` | `client_secret` is encrypted before the JSON config is written to the database |
| **Use** | `plugin_service.request_auth_token` | Secret is decrypted before being passed to `OAuth2Client` |
| **Use** | `PluginServiceAutoComplete._get_access_token` | Secret is decrypted before being passed to `OAuth2Client` |

Encrypted values are stored with a `fernet:` prefix (e.g. `fernet:gAAAAAB...`). Values without this prefix are passed through unchanged — this ensures **backward compatibility** with secrets already stored in plaintext.

### Setup

Generate a Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add it to `.env.local`:

```
GC_SECRET_ENCRYPTION_KEY=<generated-key>
```

### The `SecretCipher` class

The encryption logic lives in `ina_ground_control/utils/crypto.py`. The class is designed for full testability — it takes the key as a constructor argument, with no dependency on application settings:

```python
from cryptography.fernet import Fernet
from ina_ground_control.utils.crypto import SecretCipher

key = Fernet.generate_key().decode()
cipher = SecretCipher(key)

encrypted = cipher.encrypt("my-secret")   # "fernet:gAAAAAB..."
plain     = cipher.decrypt(encrypted)     # "my-secret"
plain     = cipher.decrypt("legacy")      # "legacy"  ← passthrough, no prefix
```

Use `get_secret_cipher()` in application code to get an instance pre-loaded from settings:

```python
from ina_ground_control.utils.crypto import get_secret_cipher

cipher = get_secret_cipher()
plain  = cipher.decrypt(config.client_secret)
```

### Writing tests

Instantiate `SecretCipher` directly with a test key — no environment variable or settings mock needed:

```python
from cryptography.fernet import Fernet
from ina_ground_control.utils.crypto import SecretCipher

def test_encrypt_decrypt_roundtrip():
    cipher = SecretCipher(Fernet.generate_key().decode())
    secret = "my-test-secret"
    assert cipher.decrypt(cipher.encrypt(secret)) == secret

def test_plaintext_passthrough():
    cipher = SecretCipher(Fernet.generate_key().decode())
    assert cipher.decrypt("legacy-plain") == "legacy-plain"

def test_is_encrypted():
    cipher = SecretCipher(Fernet.generate_key().decode())
    assert SecretCipher.is_encrypted(cipher.encrypt("x")) is True
    assert SecretCipher.is_encrypted("plain") is False
```
