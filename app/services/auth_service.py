"""Regras de autenticacao."""
from app.exceptions.domain import CredenciaisInvalidasError
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, users: UserRepository | None = None) -> None:
        self._users = users or UserRepository()

    def authenticate(self, login: str, senha: str) -> User:
        """Valida as credenciais e devolve o usuario autenticado.

        Levanta CredenciaisInvalidasError quando o usuario nao existe ou a
        senha nao confere. A mesma excecao para os dois casos evita revelar
        qual dos campos estava errado.
        """
        user = self._users.find_by_login(login)
        if user is None or not user.check_password(senha):
            raise CredenciaisInvalidasError()
        return user
