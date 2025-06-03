from functools import wraps
from typing import Callable, Any

import aiogram.utils.markdown as md
from aiogram.enums import ParseMode
from aiogram.types import Message


def validate_command(params=None, min_args: int = 1):
    """
    A decorator that validates a command has the required parameters.
    If validation fails, sends an error message and prevents handler execution.

    Args:
        params: List of parameter specifications, each with name, type, and description
                Example: [{"name": "name", "type": str, "description": "User's name"},
                          {"name": "age", "type": int, "description": "User's age"}]
        min_args: Minimum number of arguments required (excluding the command itself)
    """
    if params is None:
        params = []

    def decorator(handler_func: Callable) -> Callable:
        @wraps(handler_func)
        async def wrapper(message: Message, *args, **kwargs) -> Any:
            command_parts = message.text.split()
            command = command_parts[0] if command_parts else ""
            command_args = command_parts[1:] if len(command_parts) > 0 else []

            # Check for minimum args requirement
            if len(command_args) < min_args:
                # Generate help text with parameter descriptions
                help_text = md.text(
                    md.hbold(f"This command requires at least {min_args} argument{'s' if min_args > 1 else ''}."),
                )

                if params:
                    help_text += "\n\n" + md.hbold("Parameters:") + "\n"
                    for param in params:
                        name = param.get('name', '').lower()
                        desc = param.get('description', '')
                        param_type = param.get('type', str).__name__
                        help_text += f"- {name} ({param_type}): {desc}\n"

                    # Add usage examples
                    help_text += "\n" + md.hbold("Example formats:") + "\n"
                    # Positional example
                    positional = f"{command}"
                    for param in params:
                        positional += f" <{param.get('name')}>"
                    help_text += f"1. {positional}\n\n"

                    # Key-value example
                    key_value = f"{command}\n"
                    for param in params:
                        key_value += f"{param.get('name')}: <value>\n"
                    help_text += f"2. {key_value}"

                await message.answer(
                    text=help_text,
                    parse_mode=ParseMode.HTML,
                )
                return None

            # Parse arguments based on format
            param_dict = {}

            # Check if message uses key-value format
            message_text = message.text.strip()
            if '\n' in message_text and ':' in message_text:
                # Key-value format (name: value)
                lines = message_text.split('\n')
                for line in lines[1:]:  # Skip the command line
                    if ':' in line:
                        key, value = line.split(':', 1)
                        param_dict[key.strip()] = value.strip()
            elif params:
                # Positional format - map arguments to parameter names
                for i, param in enumerate(params):
                    if i < len(command_args):
                        param_dict[param.get('name')] = command_args[i]

            # Convert parameters to their specified types
            for param in params:
                name = param.get('name')
                param_type = param.get('type', str)
                if name in param_dict:
                    try:
                        param_dict[name] = param_type(param_dict[name])
                    except ValueError:
                        await message.answer(
                            text=md.text(
                                md.hbold(f"Invalid value for '{name}'. Expected {param_type.__name__}."),
                            ),
                            parse_mode=ParseMode.HTML,
                        )
                        return None

            # Call the handler with both original args and the parsed parameters
            return await handler_func(message, command_args, *args, **param_dict, **kwargs)

        return wrapper

    return decorator
