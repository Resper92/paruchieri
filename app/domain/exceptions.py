class DomainError(Exception):
    """Base class for all domain-level errors."""


class NotFoundError(DomainError):
    """Raised when a requested entity does not exist."""


class PermissionDeniedError(DomainError):
    """Raised when the current user is not allowed to perform an action."""


class ConflictError(DomainError):
    """Raised for uniqueness/state conflicts (e.g. duplicate email)."""


class InvalidCredentialsError(DomainError):
    """Raised on failed authentication."""
