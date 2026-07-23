from app.domain.entities.user import User
from app.domain.exceptions import NotFoundError
from app.domain.policies import ensure_role
from app.domain.repositories.user_repository import UserRepository
from app.domain.role import Role


class ListUsersUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    def execute(self, current_user: User, skip: int = 0, limit: int = 100) -> list[User]:
        ensure_role(current_user, Role.SUPERADMIN)
        return self._users.get_multi(skip=skip, limit=limit)


class UpdateUserRoleUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    def execute(self, current_user: User, user_id: int, new_role: Role) -> User:
        ensure_role(current_user, Role.SUPERADMIN)

        target = self._users.get(user_id)
        if target is None:
            raise NotFoundError("User not found")

        target.role = new_role
        return self._users.update(target)
