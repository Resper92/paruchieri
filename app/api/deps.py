from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.application.ports import PasswordHasher, TokenService
from app.application.use_cases.admin import ListUsersUseCase, UpdateUserRoleUseCase
from app.application.use_cases.appointments import (
    BookAppointmentUseCase,
    GetAppointmentUseCase,
    ListAppointmentsUseCase,
)
from app.application.use_cases.auth import AuthenticateUserUseCase, RegisterUserUseCase
from app.application.use_cases.salons import CreateSalonUseCase, GetSalonUseCase, ListSalonsUseCase
from app.application.use_cases.services import (
    CreateServiceUseCase,
    GetServiceUseCase,
    ListServicesUseCase,
)
from app.application.use_cases.staff import CreateStaffUseCase, GetStaffUseCase, ListStaffUseCase
from app.domain.entities.user import User
from app.infrastructure.config import settings
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.appointment_repository import SqlAlchemyAppointmentRepository
from app.infrastructure.repositories.salon_repository import SqlAlchemySalonRepository
from app.infrastructure.repositories.service_repository import SqlAlchemyServiceRepository
from app.infrastructure.repositories.staff_repository import SqlAlchemyStaffRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.security import BcryptPasswordHasher, JwtTokenService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_password_hasher = BcryptPasswordHasher()
_token_service = JwtTokenService(
    secret_key=settings.secret_key, expire_minutes=settings.access_token_expire_minutes
)


def get_password_hasher() -> PasswordHasher:
    return _password_hasher


def get_token_service() -> TokenService:
    return _token_service


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    token_service: TokenService = Depends(get_token_service),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email = token_service.decode_subject(token)
    except Exception as exc:
        raise credentials_exception from exc

    user = SqlAlchemyUserRepository(db).get_by_email(email)
    if user is None:
        raise credentials_exception
    return user


# --- use case factories (composition root) --------------------------------


def get_register_user_use_case(
    db: Session = Depends(get_db),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(SqlAlchemyUserRepository(db), password_hasher)


def get_authenticate_user_use_case(
    db: Session = Depends(get_db),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(SqlAlchemyUserRepository(db), password_hasher, token_service)


def get_create_salon_use_case(db: Session = Depends(get_db)) -> CreateSalonUseCase:
    return CreateSalonUseCase(SqlAlchemySalonRepository(db))


def get_list_salons_use_case(db: Session = Depends(get_db)) -> ListSalonsUseCase:
    return ListSalonsUseCase(SqlAlchemySalonRepository(db))


def get_salon_use_case(db: Session = Depends(get_db)) -> GetSalonUseCase:
    return GetSalonUseCase(SqlAlchemySalonRepository(db))


def get_create_staff_use_case(db: Session = Depends(get_db)) -> CreateStaffUseCase:
    return CreateStaffUseCase(SqlAlchemyStaffRepository(db), SqlAlchemySalonRepository(db))


def get_list_staff_use_case(db: Session = Depends(get_db)) -> ListStaffUseCase:
    return ListStaffUseCase(SqlAlchemyStaffRepository(db))


def get_staff_use_case(db: Session = Depends(get_db)) -> GetStaffUseCase:
    return GetStaffUseCase(SqlAlchemyStaffRepository(db))


def get_create_service_use_case(db: Session = Depends(get_db)) -> CreateServiceUseCase:
    return CreateServiceUseCase(SqlAlchemyServiceRepository(db), SqlAlchemySalonRepository(db))


def get_list_services_use_case(db: Session = Depends(get_db)) -> ListServicesUseCase:
    return ListServicesUseCase(SqlAlchemyServiceRepository(db))


def get_service_use_case(db: Session = Depends(get_db)) -> GetServiceUseCase:
    return GetServiceUseCase(SqlAlchemyServiceRepository(db))


def get_book_appointment_use_case(db: Session = Depends(get_db)) -> BookAppointmentUseCase:
    return BookAppointmentUseCase(SqlAlchemyAppointmentRepository(db))


def get_list_appointments_use_case(db: Session = Depends(get_db)) -> ListAppointmentsUseCase:
    return ListAppointmentsUseCase(SqlAlchemyAppointmentRepository(db))


def get_appointment_use_case(db: Session = Depends(get_db)) -> GetAppointmentUseCase:
    return GetAppointmentUseCase(SqlAlchemyAppointmentRepository(db))


def get_list_users_use_case(db: Session = Depends(get_db)) -> ListUsersUseCase:
    return ListUsersUseCase(SqlAlchemyUserRepository(db))


def get_update_user_role_use_case(db: Session = Depends(get_db)) -> UpdateUserRoleUseCase:
    return UpdateUserRoleUseCase(SqlAlchemyUserRepository(db))
