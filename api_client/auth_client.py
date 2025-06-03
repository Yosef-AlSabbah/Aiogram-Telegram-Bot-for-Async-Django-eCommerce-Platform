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
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{cls.BASE_URL}token/create/", json=credentials
            ) as response:
                data = await cls._extract_data(response)
                token_data = data.get("data", {})
                access = token_data.get("access")
                refresh = token_data.get("refresh")
                telegram_id = credentials.get("telegram_id", "unknown")
                pool = await RedisConnection.get_pool()
                # I have to delete every redis entry associated with the telegram_id
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

        # Remove tokens from Redis cache regardless of API call
        await pool.delete(f"{TokenPrefix.ACCESS.value}{telegram_id}", f"{TokenPrefix.REFRESH.value}{telegram_id}")

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
        pool = await RedisConnection.get_pool()

        # Define a timeout for caching the is_staff status
        IS_STAFF_TIMEOUT: Final[int] = 3600

        # Try to get from cache first
        cached_result = await pool.get(f"{TokenPrefix.IS_STAFF.value}{telegram_id}")
        if cached_result is not None:
            return cached_result == "True"

        # Make API request to check staff status
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{cls.BASE_URL}me/is-staff/",
                    params={"telegram_id": telegram_id}
            ) as response:
                try:
                    data = await cls._extract_data(response)
                    is_staff = data.get("is_staff", False)
                except ApiClientError:
                    # Log the error or handle it appropriately
                    is_staff = False

                # Cache the result for one hour
                await pool.set(f"{TokenPrefix.IS_STAFF.value}{telegram_id}", str(is_staff), ex=IS_STAFF_TIMEOUT)

                return is_staff
