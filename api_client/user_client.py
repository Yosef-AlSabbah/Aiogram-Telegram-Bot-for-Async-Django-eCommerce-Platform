import functools

import aiohttp

from api.structure.models import User
from .exceptions.common import ApiClientError
from config import settings


class UserClient:
    """
    Asynchronous client for interacting with the user management API.
    Provides methods to get, update, and delete users.
    """

    BASE_URL = settings.USERS_API_URL

    @staticmethod
    def _handle_user_response(many: bool = False):
        """
        Decorator to handle user API responses.
        Parses the response and returns User instances or a list of Users.
        """

        def decorator(func):
            @functools.wraps(func)
            async def wrapper(self, *args, **kwargs):
                async with aiohttp.ClientSession() as session:
                    async with await func(self, session, *args, **kwargs) as response:
                        data = await self._extract_data(response)
                        if many:
                            return [self._create_user_from_data(user) for user in data]
                        return self._create_user_from_data(data)

            return wrapper

        return decorator

    @staticmethod
    async def _extract_data(response: aiohttp.ClientResponse) -> dict:
        """
        Extracts and returns the 'data' field from the API response.
        Raises ApiClientError if the response indicates failure.
        """
        response_json = await response.json()
        if not response_json.get("success", True):
            raise ApiClientError(response_json.get("message", "Unknown error"))
        return response_json.get("data", {})

    @staticmethod
    def _create_user_from_data(data: dict) -> User:
        """
        Instantiates a User object from a dictionary of user data.
        """
        return User(**data)

    @classmethod
    @_handle_user_response
    async def get_user(cls, session, user_id: str):
        """
        Retrieves a single user by user ID.
        """
        return session.get(f"{cls.BASE_URL}/{user_id}/")

    @classmethod
    @_handle_user_response(many=True)
    async def get_users(cls, session, **params):
        """
        Retrieves a list of users, optionally filtered by query parameters.
        """
        return session.get(cls.BASE_URL, params=params)

    @classmethod
    @_handle_user_response
    async def update_user(cls, session, user_id: str, user_data: dict):
        """
        Updates a user's information.
        """
        return session.patch(f"{cls.BASE_URL}/{user_id}/", json=user_data)

    @classmethod
    @_handle_user_response
    async def delete_user(cls, session, user_id: str):
        """
        Deletes a user by user ID.
        Returns None if deletion is successful (HTTP 204).
        """
        response = await session.delete(f"{cls.BASE_URL}/{user_id}/")
        if response.status == 204:
            return None
        return response
