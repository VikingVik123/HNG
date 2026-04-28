class APIException(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidRequestException(APIException):
    """400 Bad Request"""
    def __init__(self, message: str):
        super().__init__(message, 400)


class InvalidTypeException(APIException):
    """422 Unprocessable Entity"""
    def __init__(self, message: str):
        super().__init__(message, 422)


class ProfileNotFoundException(APIException):
    """404 Not Found"""
    def __init__(self, message: str = "Profile not found"):
        super().__init__(message, 404)


class ExternalAPIException(APIException):
    """502 Bad Gateway - External API error"""
    def __init__(self, api_name: str):
        message = f"{api_name} returned an invalid response"
        super().__init__(message, 502)


class ServerException(APIException):
    """500 Internal Server Error"""
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, 500)

class UnauthorizedException(APIException):
    """401 Unauthorized"""
    def __init__(self, message: str = "Unauthorized: Invalid or missing credentials"):
        super().__init__(message, 401)

class ForbiddenException(APIException):
    """403 Forbidden"""
    def __init__(self, message: str = "Token valid but insufficient permissions"):
        super().__init__(message, 403)

class InvalidTokenException(APIException):
    """401 Unauthorized - Invalid token"""
    def __init__(self, message: str = "Malformed or invalid token"):
        super().__init__(message, 401)

class UserNotActiveException(APIException):
    """403 Forbidden - User account is inactive"""
    def __init__(self, message: str = "User account is inactive"):
        super().__init__(message, 403)


class GitHubOAuthException(APIException):
    """502 Bad Gateway - GitHub OAuth error"""
    def __init__(self, message: str = "GitHub OAuth service error"):
        super().__init__(message, 502)