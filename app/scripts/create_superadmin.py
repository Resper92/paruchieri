"""Create or promote a superadmin user.

Self-registration cannot create superadmin accounts (see /auth/register),
so the first superadmin must be seeded directly against the database.

Usage:
    python -m app.scripts.create_superadmin --email admin@example.com --password ChangeMe123!
"""
import argparse

from app.domain.entities.user import User
from app.domain.role import Role
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.security import BcryptPasswordHasher


def create_superadmin(email: str, password: str) -> None:
    hasher = BcryptPasswordHasher()
    db = SessionLocal()
    try:
        repository = SqlAlchemyUserRepository(db)
        existing = repository.get_by_email(email)
        if existing is None:
            repository.add(
                User(id=None, email=email, password_hash=hasher.hash(password), role=Role.SUPERADMIN)
            )
            action = "Created"
        else:
            existing.role = Role.SUPERADMIN
            existing.password_hash = hasher.hash(password)
            repository.update(existing)
            action = "Promoted existing user to"
        print(f"{action} superadmin: {email}")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    create_superadmin(args.email, args.password)


if __name__ == "__main__":
    main()
