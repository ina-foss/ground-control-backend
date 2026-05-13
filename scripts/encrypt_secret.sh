#!/usr/bin/env bash
# encrypt_secret.sh
# Encrypts a plaintext value using the Fernet key from .env.local
# Usage:
#   ./scripts/encrypt_secret.sh <plaintext>
#   echo "mySecret" | ./scripts/encrypt_secret.sh

set -euo pipefail

ENV_FILE=".env.local"
KEY_VAR="GC_SECRET_ENCRYPTION_KEY"

# Load the key from .env.local
if [[ ! -f "${ENV_FILE}" ]]; then
    echo "❌  ${ENV_FILE} not found. Run ./scripts/generate_fernet_key.sh first." >&2
    exit 1
fi

KEY=$(grep "^${KEY_VAR}=" "${ENV_FILE}" | cut -d '=' -f2-)

if [[ -z "${KEY}" ]]; then
    echo "❌  ${KEY_VAR} not found in ${ENV_FILE}. Run ./scripts/generate_fernet_key.sh first." >&2
    exit 1
fi

# Read plaintext from argument or stdin
if [[ $# -ge 1 ]]; then
    PLAINTEXT="$1"
elif [[ ! -t 0 ]]; then
    PLAINTEXT=$(cat)
else
    echo "Usage: $0 <plaintext>" >&2
    echo "       echo 'mySecret' | $0" >&2
    exit 1
fi

python - <<EOF
from cryptography.fernet import Fernet

key = "${KEY}"
plain = """${PLAINTEXT}"""

cipher = Fernet(key.encode())
encrypted = "fernet:" + cipher.encrypt(plain.encode()).decode()
print(encrypted)
EOF
