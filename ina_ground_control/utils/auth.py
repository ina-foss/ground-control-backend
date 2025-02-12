from jose import jwt
from fastapi import HTTPException, Header
from typing import List, Union
from fastapi_keycloak_middleware import (MatchStrategy)
from functools import wraps

class TokenService:
    @staticmethod
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
            # Decode the JWT token without verifying signature, audience, or expiration.
            payload = jwt.decode(token, key=None, options={"verify_signature": False, "verify_aud": False, "verify_exp": False})

            # Extract roles from the "realm_access" field (if present)
            roles = []
            if "realm_access" in payload:
                roles.extend(payload["realm_access"].get("roles", []))

            # Get user email
            user_email = payload.get("email", None)

            # Raise exception if email is not found
            if not user_email:
                raise HTTPException(status_code=400, detail="Email not found in the token")

            return {
                "roles": roles,
                "email": user_email
            }

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    @staticmethod
    def get_token_from_request(authorization: str = Header(None)) -> str:
        """
        Extract the token from the Authorization header.

        Args:
            authorization (str): The Authorization header.

        Returns:
            str: The extracted JWT token.

        Raises:
            HTTPException: If the Authorization header is missing or the token type is invalid.
        """
        if authorization is None:
            raise HTTPException(status_code=400, detail="Authorization header missing")

        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=400, detail="Invalid token type. Expected Bearer")

        token = authorization.split("Bearer ")[-1]
        return token

def require_role(roles: Union[str, List[str]], match_strategy: MatchStrategy = MatchStrategy.AND):
    if isinstance(roles, str):
        roles = [roles]

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            token = kwargs.get('token', None)
            user_roles  = TokenService.get_user_info_from_token(token)["roles"]
            print("token",token)
            print("roles",user_roles)
            if user_roles is None:
                raise HTTPException(status_code=403, detail="User roles not provided")

            if match_strategy == MatchStrategy.AND:
                if not all(role in user_roles for role in roles):
                    raise HTTPException(status_code=403, detail="Insufficient roles")
            elif match_strategy == MatchStrategy.OR:
                if not any(role in user_roles for role in roles):
                    raise HTTPException(status_code=403, detail="Insufficient roles")

            return await func(*args, **kwargs)

        return wrapper

    return decorator