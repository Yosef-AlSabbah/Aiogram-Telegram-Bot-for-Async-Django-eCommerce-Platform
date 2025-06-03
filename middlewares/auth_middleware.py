from api.structure.models import User
from routers.auth.utils.commons import get_auth_token


class AuthMiddleware:
    """
    Middleware for checking authentication and adding auth headers.
    If access token is missing but refresh token exists, it will try to refresh.
    """

    @staticmethod
    async def __call__(handler, event, data):
        # Extract telegram_id from the message
        user = getattr(event, 'from_user', None)
        if user and isinstance(user, User):
            token = await get_auth_token(user.id)
            if token:
                # Add to middleware data to be used in API calls
                data["auth_header"] = f"Bearer {token}"

        # Continue processing
        return await handler(event, data)
