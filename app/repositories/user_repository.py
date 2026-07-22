"""Acesso a dados de usuario. Unico ponto que consulta a tabela users."""
import logging

from sqlalchemy.exc import SQLAlchemyError

from app.exceptions.domain import BancoIndisponivelError
from app.extensions import db
from app.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Fronteira do banco: traduz falhas de infra em erro de dominio."""

    def find_by_login(self, login: str) -> User | None:
        """Busca por username OU email."""
        try:
            return User.query.filter(
                (User.username == login) | (User.email == login)
            ).first()
        except SQLAlchemyError as exc:
            logger.error("Falha ao consultar usuario no banco: %s", exc)
            raise BancoIndisponivelError() from exc

    def save(self, user: User) -> User:
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except SQLAlchemyError as exc:
            db.session.rollback()
            logger.error("Falha ao gravar usuario no banco: %s", exc)
            raise BancoIndisponivelError() from exc
