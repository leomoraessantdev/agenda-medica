"""Rotas de autenticacao. Apenas orquestracao HTTP; regra de negocio no service."""
import logging

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app import messages
from app.exceptions.domain import BancoIndisponivelError, CredenciaisInvalidasError
from app.services.auth_service import AuthService
from app.utils.security import validate_csrf

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)
_auth_service = AuthService()


@auth_bp.route("/")
def index():
    return redirect(url_for("agenda.agenda"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("agenda.agenda"))
        return render_template("login.html")

    if not validate_csrf(request.form.get("_csrf_token")):
        flash(messages.SESSAO_EXPIRADA, "error")
        return render_template("login.html"), 400

    login_input = request.form.get("login", "").strip()
    senha = request.form.get("senha", "")

    if not login_input or not senha:
        flash(messages.CAMPOS_LOGIN_OBRIGATORIOS, "error")
        return render_template("login.html", login=login_input), 400

    try:
        user = _auth_service.authenticate(login_input, senha)
    except CredenciaisInvalidasError:
        logger.warning("Tentativa de login invalida para '%s'.", login_input)
        flash(messages.CREDENCIAIS_INVALIDAS, "error")
        return render_template("login.html", login=login_input), 401
    except BancoIndisponivelError:
        logger.error("Login indisponivel: falha de acesso ao banco de dados.")
        flash(messages.BANCO_INDISPONIVEL, "error")
        return render_template("login.html", login=login_input), 503

    session.clear()
    session["user_id"] = user.id
    session["username"] = user.username
    flash(f"Bem-vindo, {user.username}.", "success")
    return redirect(url_for("agenda.agenda"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    if not validate_csrf(request.form.get("_csrf_token")):
        flash(messages.SESSAO_EXPIRADA, "error")
        return redirect(url_for("agenda.agenda"))
    session.clear()
    flash("Sessao encerrada.", "success")
    return redirect(url_for("auth.login"))
