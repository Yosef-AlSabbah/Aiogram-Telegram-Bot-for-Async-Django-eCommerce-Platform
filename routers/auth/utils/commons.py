from typing import Optional

from api_client.auth_client import TokenPrefix, AuthClient
from redis_client.connection import RedisConnection


async def is_user_authenticated(telegram_id: int) -> bool:
    """
    Check if the user is authenticated.
    Returns True if the user is authenticated, otherwise False.
    """
    pool = await RedisConnection.get_pool()
    # Check if access token exists for this user
    access_token = await pool.get(f"{TokenPrefix.ACCESS.value}{telegram_id}")
    if access_token:
        return True

    # Check if refresh token exists
    refresh_token = await pool.get(f"{TokenPrefix.REFRESH.value}{telegram_id}")
    return refresh_token is not None


async def get_auth_token(telegram_id: int) -> Optional[str]:
    """
    Get or refresh the user's access token.
    Returns the token if found or refreshed, None otherwise.
    """
    pool = await RedisConnection.get_pool()

    # Try to get access token first
    access_token = await pool.get(f"{TokenPrefix.ACCESS.value}{telegram_id}")
    if access_token:
        return access_token.decode('utf-8')

    # If no access token, try to refresh using refresh token
    refresh_token = await pool.get(f"{TokenPrefix.REFRESH.value}{telegram_id}")
    if refresh_token:
        try:
            # Refresh the token
            refresh_data = {
                "refresh": refresh_token.decode('utf-8'),
                "telegram_id": str(telegram_id)
            }
            token_data = await AuthClient.refresh_token(refresh_data)

            # Return the new access token
            if token_data and "access" in token_data:
                return token_data["access"]
        except Exception:
            # If refresh fails, return None
            pass

    return None
