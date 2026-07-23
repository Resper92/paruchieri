from app.domain.entities.salon import Salon
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDeniedError
from app.domain.role import Role


def ensure_role(user: User, *roles: Role) -> None:
    if not user.has_any_role(*roles):
        raise PermissionDeniedError("You do not have permission to perform this action")


def ensure_can_manage_salon(user: User, salon: Salon) -> None:
    if user.role != Role.SUPERADMIN and not salon.is_owned_by(user.id):
        raise PermissionDeniedError("You do not own this salon")
