from jose import jwt
from fastapi import HTTPException, Header
from typing import List

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
