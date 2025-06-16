import json
from typing import List, Dict, Any, Optional
from redis_client.connection import RedisConnection


class ConversationHistoryManager:
    """Manages user conversation history with the AI assistant using Redis"""

    def __init__(self, max_history_length: int = 10):
        """Initialize with a maximum number of messages to keep in history"""
        self.max_history_length = max_history_length

    async def get_conversation_history(self, user_id: int) -> List[Dict[str, str]]:
        """Retrieve the conversation history for a specific user"""
        pool = await RedisConnection.get_pool()
        history_key = f"user:{user_id}:conversation_history"

        # Get the history from Redis
        history_json = await pool.get(history_key)
        if not history_json:
            return []

        try:
            return json.loads(history_json)
        except json.JSONDecodeError:
            return []

    async def add_message(self, user_id: int, message: Dict[str, str]) -> None:
        """Add a message to the user's conversation history

        Args:
            user_id: The telegram user ID
            message: Dictionary with 'role' and 'content' keys
        """
        pool = await RedisConnection.get_pool()
        history_key = f"user:{user_id}:conversation_history"

        # Get existing history
        history = await self.get_conversation_history(user_id)

        # Add new message and trim to max length
        history.append(message)
        if len(history) > self.max_history_length:
            # Keep system message if it exists at the beginning,
            # then the most recent messages up to max_history_length
            system_message = None
            if history and history[0]["role"] == "system":
                system_message = history[0]
                history = history[1:]

            # Trim the history
            history = history[-(self.max_history_length - (1 if system_message else 0)):]

            # Add system message back if it existed
            if system_message:
                history = [system_message] + history

        # Save updated history
        await pool.set(history_key, json.dumps(history))

        # Set expiry for the conversation history (7 days)
        await pool.expire(history_key, 60 * 60 * 24 * 7)

    async def clear_history(self, user_id: int) -> None:
        """Clear the conversation history for a user"""
        pool = await RedisConnection.get_pool()
        history_key = f"user:{user_id}:conversation_history"
        await pool.delete(history_key)
