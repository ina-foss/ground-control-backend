#!/usr/bin/env bash
# generate_fernet_key.sh
# Generates a Fernet encryption key and appends it to .env.local
# Usage:
#   ./scripts/generate_fernet_key.sh            # append to .env.local
#   ./scripts/generate_fernet_key.sh --print    # print only, do not write

set -euo pipefail

ENV_FILE=".env.local"
KEY_VAR="GC_SECRET_ENCRYPTION_KEY"

KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

if [[ "${1:-}" == "--print" ]]; then
    echo "${KEY_VAR}=${KEY}"
    exit 0
fi

if grep -q "^${KEY_VAR}=" "${ENV_FILE}" 2>/dev/null; then
    echo "⚠️  ${KEY_VAR} already exists in ${ENV_FILE} — not overwriting."
    echo "   Delete the existing line first, then re-run this script."
    exit 1
fi

echo "${KEY_VAR}=${KEY}" >> "${ENV_FILE}"
echo "✅  Key written to ${ENV_FILE}:"
echo "   ${KEY_VAR}=${KEY}"
