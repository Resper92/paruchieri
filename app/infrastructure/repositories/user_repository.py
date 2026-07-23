from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.infrastructure.db.models.user_model import UserModel


class SqlAlchemyUserRepository:
    """Infrastructure adapter implementing the UserRepository port."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, user_id: int) -> User | None:
        model = self._db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        model = self._db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[User]:
        models = self._db.query(UserModel).offset(skip).limit(limit).all()
        return [self._to_entity(model) for model in models]

    def add(self, user: User) -> User:
        model = UserModel(email=user.email, password_hash=user.password_hash, role=user.role)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def update(self, user: User) -> User:
        model = self._db.query(UserModel).filter(UserModel.id == user.id).first()
        model.email = user.email
        model.password_hash = user.password_hash
        model.role = user.role
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            role=model.role,
        )
