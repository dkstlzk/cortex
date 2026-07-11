import os
import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.shared.exceptions import AuthenticationError

security_scheme = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """
    Validates a JWT against a remote JWKS URL. 
    Production deployments must set the JWKS_URL environment variable.
    """
    token = credentials.credentials
    jwks_url = os.getenv("JWKS_URL")
    
    if not jwks_url:
        # Fail closed if security is not configured
        raise AuthenticationError("Authentication provider (JWKS_URL) not configured.")
        
    try:
        jwks_client = jwt.PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        audience = os.getenv("JWT_AUDIENCE")
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience
        )
        return payload
    except jwt.PyJWKClientError as e:
        raise AuthenticationError(f"Unable to fetch signing keys: {str(e)}")
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")
    except Exception as e:
        raise AuthenticationError(f"Authentication failed: {str(e)}")
