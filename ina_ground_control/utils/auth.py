from jose import jwt
from fastapi import HTTPException
from typing import List
from fastapi import HTTPException

def get_user_info_from_token(token: str) -> dict:
    """
    Extract roles and user email from the JWT token.

    Args:
        token (str): The JWT token (Bearer token) from headers.

    Returns:
        dict: A dictionary containing:
              - 'roles': List of roles extracted from the token.
              - 'user_email': User's email extracted from the token.
    """
    try:

        payload = jwt.decode(token, key=None, options={"verify_signature": False})

        # Extract roles from the "realm_access" field (if present)
        roles = []
        if "realm_access" in payload:
            roles.extend(payload["realm_access"].get("roles", []))

        user_email = payload.get("email", None)

        if not user_email:
            raise HTTPException(status_code=400, detail="Email not found in the token")

        return {
            "roles": roles,
            "user_email": user_email
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")