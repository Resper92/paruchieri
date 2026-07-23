from app.application.ports import PasswordHasher, TokenService
from app.domain.entities.user import User
from app.domain.exceptions import ConflictError, InvalidCredentialsError
from app.domain.repositories.user_repository import UserRepository
from app.domain.role import Role


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher) -> None:
        self._users = user_repository
        self._hasher = password_hasher

    def execute(self, email: str, password: str, role: Role) -> User:
        if role == Role.SUPERADMIN:
            raise ConflictError("Cannot self-register as superadmin")
        if self._users.get_by_email(email) is not None:
            raise ConflictError("Email already registered")

        user = User(id=None, email=email, password_hash=self._hasher.hash(password), role=role)
        return self._users.add(user)


class AuthenticateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._users = user_repository
        self._hasher = password_hasher
        self._tokens = token_service

    def execute(self, email: str, password: str) -> str:
        user = self._users.get_by_email(email)
        if user is None or not self._hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError("Incorrect email or password")
        return self._tokens.create_access_token(subject=user.email)
