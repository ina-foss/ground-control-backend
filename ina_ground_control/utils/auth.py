import jwt
from fastapi import HTTPException

def get_current_user_role(token: str) -> list:
    """
    Extract roles from the JWT token.

    Args:
        token (str): The JWT token (Bearer token) from headers

    Returns:
        list: A list of roles extracted from the token.
    """
    try:
        # Decode the JWT token (without verifying the signature in this case)
        payload = jwt.decode(token, options={"verify_signature": False})

        # Initialize an empty list to store roles
        roles = []

        # Extract roles from realm_access
        if "realm_access" in payload:
            roles.extend(payload["realm_access"].get("roles", []))

        # Extract roles from resource_access (if present)
        #if "resource_access" in payload:
        #    for resource in payload["resource_access"].values():
        #       roles.extend(resource.get("roles", []))

        return roles

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
