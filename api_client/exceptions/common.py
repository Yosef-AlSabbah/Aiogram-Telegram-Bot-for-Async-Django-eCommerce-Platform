class ApiClientError(Exception):
    """
    Exception raised for errors returned by the API client.

    :param:
        message (str): Description of the error.
        response_errors (Any, optional): Additional error details from the API response.
    """

    def __init__(self, message: str, response_errors=None):
        super().__init__(message)
        # Store additional error details from the API response, if any
        self.response_errors = response_errors
