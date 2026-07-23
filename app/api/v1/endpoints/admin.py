from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_list_users_use_case, get_update_user_role_use_case
from app.api.v1.schemas.user import RoleUpdate, UserRead
from app.application.use_cases.admin import ListUsersUseCase, UpdateUserRoleUseCase
from app.domain.entities.user import User

router = APIRouter()


@router.get("/users", response_model=list[UserRead])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
) -> list[UserRead]:
    users = use_case.execute(current_user, skip=skip, limit=limit)
    return [UserRead.model_validate(user) for user in users]


@router.patch("/users/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: int,
    payload: RoleUpdate,
    current_user: User = Depends(get_current_user),
    use_case: UpdateUserRoleUseCase = Depends(get_update_user_role_use_case),
) -> UserRead:
    updated = use_case.execute(current_user, user_id, payload.role)
    return UserRead.model_validate(updated)
