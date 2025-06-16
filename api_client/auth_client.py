from enum import Enum
from typing import Final

import aiohttp

from api_client.exceptions.common import ApiClientError
from config import settings
from redis_client.connection import RedisConnection


class TokenPrefix(Enum):
    ACCESS = "access_token:"
    REFRESH = "refresh_token:"
    IS_STAFF = "is_staff:"


class AuthClient:
    BASE_URL = settings.AUTH_API_URL

    @staticmethod
    async def _extract_data(response: aiohttp.ClientResponse) -> dict:
        response_json = await response.json()
        if not response_json.get("success", True):
            raise ApiClientError(
                message=response_json.get("message", "Unknown error"),
                response_errors=response_json.get("errors", {}), )
        return response_json.get("data", {})

    @classmethod
    async def register(cls, user_data: dict):
        """
        POST /api/v1/auth/register/
        Registers a new user.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{cls.BASE_URL}register/", json=user_data
            ) as response:
                return await cls._extract_data(response)

    @classmethod
    async def create_token(cls, credentials: dict):
        """
        POST /api/v1/auth/token/create/
        Creates access and refresh tokens.
        Caches both tokens using telegram id if provided.
        """
        telegram_id = credentials.get("telegram_id", "unknown")

        # First, remove all keys containing the telegram_id from Redis
        pool = await RedisConnection.get_pool()
        await cls._cleanup_telegram_id_keys(pool, telegram_id)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{cls.BASE_URL}token/create/", json=credentials
            ) as response:
                data = await cls._extract_data(response)
                token_data = data.get("data", {})
                access = token_data.get("access")
                refresh = token_data.get("refresh")

                # Cache tokens for one hour (3600 seconds); adjust expiration as needed.
                if access:
                    await pool.set(
                        f"{TokenPrefix.ACCESS.value}{telegram_id}",
                        access,
                        ex=settings.ACCESS_TOKEN_LIFETIME,
                    )
                if refresh:
                    await pool.set(
                        f"{TokenPrefix.REFRESH.value}{telegram_id}",
                        refresh,
                        ex=settings.REFRESH_TOKEN_LIFETIME,
                    )
                return data

    @classmethod
    async def destroy_token(cls, telegram_id: int):
        """
        POST /api/v1/auth/token/destroy/
        Destroys a token and removes associated cached tokens from Redis.
        If no refresh token is available, only clears the local Redis cache.
        """
        # Get refresh token from Redis
        pool = await RedisConnection.get_pool()
        refresh_token = await pool.get(f"{TokenPrefix.REFRESH.value}{telegram_id}")

        # Only call the API if we have a valid refresh token
        if refresh_token:
            # Call API to destroy token server-side with refresh token
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{cls.BASE_URL}token/destroy/",
                        json={"refresh": refresh_token}
                ) as response:
                    result = await cls._extract_data(response)
        else:
            # No refresh token available, so return an empty result
            result = {}

        # Clean up all keys related to this telegram_id from Redis
        await cls._cleanup_telegram_id_keys(pool, telegram_id)

        return result

    @classmethod
    async def refresh_token(cls, token: dict):
        """
        POST /api/v1/auth/token/refresh/
        Refreshes tokens and caches the new refresh token in Redis.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{cls.BASE_URL}token/refresh/", json=token
            ) as response:
                data = await cls._extract_data(response)
                new_refresh = data.get("refresh")
                telegram_id = token.get("telegram_id", "unknown")
                if new_refresh:
                    pool = await RedisConnection.get_pool()
                    await pool.set(f"{TokenPrefix.REFRESH.value}{telegram_id}", new_refresh, ex=3600)
                return data

    @classmethod
    async def verify_token(cls, token: dict):
        """
        POST /api/v1/auth/token/verify/
        Verifies a token.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{cls.BASE_URL}token/verify/", json=token
            ) as response:
                return await cls._extract_data(response)

    @classmethod
    async def is_staff(cls, telegram_id: str) -> bool:
        """
        GET /api/v1/auth/me/is-staff/
        Check if the current user is staff.
        Caches the result for one hour.
        """
        print('IsStaff Checking staff status for telegram_id:', telegram_id)
        pool = await RedisConnection.get_pool()

        # Define a timeout for caching the is_staff status
        IS_STAFF_TIMEOUT: Final[int] = 3600

        # Debug information
        staff_key = f"{TokenPrefix.IS_STAFF.value}{telegram_id}"
        access_key = f"{TokenPrefix.ACCESS.value}{telegram_id}"
        print(f'Checking cached staff status with key: {staff_key}')

        # Try to get from cache first
        cached_result = await pool.get(staff_key)
        if cached_result is not None:
            is_staff_result = cached_result.decode() == "True"
            print(f'Found cached staff status: {is_staff_result}')
            return is_staff_result

        # Get access token from Redis
        access_token = await pool.get(access_key)
        if not access_token:
            # No token available, user cannot be staff
            print(f'No access token found for telegram_id: {telegram_id}')
            await pool.set(staff_key, "False", ex=IS_STAFF_TIMEOUT)
            return False

        # Decode the access token from bytes to string
        access_token = access_token.decode()
        print(f'Found access token, making API request to check staff status')

        # Make API request to check staff status with authorization
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        f"{cls.BASE_URL}me/is-staff/",
                        headers={"Authorization": f"Bearer {access_token}"}
                ) as response:
                    try:
                        data = await cls._extract_data(response)
                        is_staff = data.get("is_staff", False)
                        print(f'API response for is_staff: {is_staff}')
                    except ApiClientError as e:
                        print(f'API error when checking staff status: {str(e)}')
                        is_staff = False

                    # Cache the result for one hour
                    await pool.set(staff_key, str(is_staff), ex=IS_STAFF_TIMEOUT)
                    return is_staff
        except Exception as e:
            print(f'Exception when making staff status request: {str(e)}')
            await pool.set(staff_key, "False", ex=IS_STAFF_TIMEOUT)
            return False

    @classmethod
    async def _cleanup_telegram_id_keys(cls, pool, telegram_id: str):
        """
        Remove all keys containing the telegram_id from Redis.
        This will remove any key that contains the telegram_id, not just the predefined ones.
        """
        # Use scan_iter for pattern matching to avoid blocking Redis
        pattern = f"*{telegram_id}*"
        matching_keys = []
        print('Cleaning up Redis keys with pattern:', pattern)
        async for key in pool.scan_iter(match=pattern):
            print('Redis key:', key)
            matching_keys.append(key)

        if matching_keys:
            print(matching_keys)
            await pool.delete(*matching_keys)
