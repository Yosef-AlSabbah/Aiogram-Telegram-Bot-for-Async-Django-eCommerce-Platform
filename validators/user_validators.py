import re


def validate_username(username: str) -> (bool, str | None):
    """Validates a username against Arabic character requirements.
    Returns:
        - Tuple of (bool, str) where:
            - bool is True if username is valid, False otherwise
            - str is an error message if validation fails, empty string otherwise
    """
    # Define regex patterns for validation
    arabic_pattern = re.compile(r"^[\u0600-\u06FF_0-9]+$")  # Arabic characters only

    # Validate username length
    if len(username) > 150:
        return False, "Username must be 150 characters or fewer."

    # Validate username contains Arabic characters
    if not arabic_pattern.match(username):
        return (
            False,
            "Username must contain only Arabic characters, numbers, and underscores.",
        )

    # Validate username is not entirely numeric
    if username.isdigit():
        return False, "Username cannot be entirely numeric."

    # All validations passed
    return True, None


def validate_password(password: str) -> str | bool:
    """
    Validates a password meets minimum requirements.

    Returns:
        - True if the password is valid
        - Error message string if validation fails
    """
    # Validate password length
    if len(password) < 8:
        return "Password must be at least 8 characters long."

    # All validations passed
    return True


def validate_phone(phone: str) -> str | bool:
    """
    Validates a phone number format.

    Returns:
        - True if the phone number is valid
        - Error message string if validation fails
    """
    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r"[ \-()]", "", phone)
    # Ensure it starts with +972 or +970 and has 9 digits after the prefix
    match = re.match(r"^\+(972|970)(\d{9})$", cleaned)

    if not match:
        return "Phone number must start with +972 or +970 and have 9 digits after the prefix."

    # All validations passed
    return True


def validate_name(name: str) -> str | bool:
    """
    Validates a name to ensure it contains only Arabic characters or spaces.

    Returns:
        - True if the name is valid
        - Error message string if validation fails
    """
    # Define regex pattern for validation (Arabic characters and spaces)
    pattern = re.compile(r"^[\u0600-\u06FF\s]+$")

    # Validate name is not empty
    if not name or name.isspace():
        return "Name cannot be empty."

    # Validate name length
    if len(name) > 100:
        return "Name must be 100 characters or fewer."

    # Validate name contains only Arabic characters or spaces
    if not pattern.match(name):
        return "Name must contain only Arabic characters and spaces."

    # All validations passed
    return True
