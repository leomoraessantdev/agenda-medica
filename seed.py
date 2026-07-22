"""Seed do banco: cria as tabelas e o usuario de teste (idempotente).

Uso:
    python seed.py
"""
import os

from app import create_app
from app.extensions import db
from app.models.user import User
from app.repositories.user_repository import UserRepository


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        username = os.getenv("SEED_USER_USERNAME", "medico")
        email = os.getenv("SEED_USER_EMAIL", "medico@teste.com")
        senha = os.getenv("SEED_USER_PASSWORD", "medico123")

        repo = UserRepository()
        if repo.find_by_login(username) or repo.find_by_login(email):
            print(f"Usuario de teste ja existe: {username}")
            return

        user = User(username=username, email=email)
        user.set_password(senha)
        repo.save(user)
        print(f"Usuario de teste criado: {username} / {email}")


if __name__ == "__main__":
    main()
