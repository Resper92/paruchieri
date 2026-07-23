from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_authenticate_user_use_case, get_register_user_use_case
from app.api.v1.schemas.token import Token
from app.api.v1.schemas.user import UserCreate, UserRead
from app.application.use_cases.auth import AuthenticateUserUseCase, RegisterUserUseCase

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> UserRead:
    user = use_case.execute(email=user_in.email, password=user_in.password, role=user_in.role)
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
) -> Token:
    access_token = use_case.execute(email=form_data.username, password=form_data.password)
    return Token(access_token=access_token)
