"""Testes da autenticacao."""
import pytest

from app.extensions import db
from app.models.user import User


@pytest.fixture
def usuario(app):
    user = User(username="medico", email="medico@teste.com")
    user.set_password("segredo123")
    db.session.add(user)
    db.session.commit()
    return user


def _obter_csrf(client, url="/login"):
    """GET renderiza o form -> csrf_token() grava o token na sessao."""
    client.get(url)
    with client.session_transaction() as sess:
        return sess.get("_csrf_token")


def test_login_sucesso(client, usuario):
    token = _obter_csrf(client)
    resp = client.post(
        "/login",
        data={"login": "medico", "senha": "segredo123", "_csrf_token": token},
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/agenda")
    with client.session_transaction() as sess:
        assert sess["user_id"] == usuario.id


def test_login_por_email(client, usuario):
    token = _obter_csrf(client)
    resp = client.post(
        "/login",
        data={"login": "medico@teste.com", "senha": "segredo123", "_csrf_token": token},
    )
    assert resp.status_code == 302


def test_login_credenciais_invalidas(client, usuario):
    token = _obter_csrf(client)
    resp = client.post(
        "/login",
        data={"login": "medico", "senha": "errado", "_csrf_token": token},
    )
    assert resp.status_code == 401
    assert "invalidos" in resp.get_data(as_text=True).lower()


def test_login_campos_vazios(client):
    token = _obter_csrf(client)
    resp = client.post(
        "/login",
        data={"login": "", "senha": "", "_csrf_token": token},
    )
    assert resp.status_code == 400


def test_login_sem_csrf(client, usuario):
    resp = client.post("/login", data={"login": "medico", "senha": "segredo123"})
    assert resp.status_code == 400


def test_agenda_exige_login(client):
    resp = client.get("/agenda")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def test_logout_limpa_sessao(client, usuario):
    token = _obter_csrf(client)
    client.post(
        "/login",
        data={"login": "medico", "senha": "segredo123", "_csrf_token": token},
    )
    client.get("/agenda")  # renova o csrf para o form de logout
    with client.session_transaction() as sess:
        logout_token = sess.get("_csrf_token")
    resp = client.post("/logout", data={"_csrf_token": logout_token})
    assert resp.status_code == 302
    with client.session_transaction() as sess:
        assert "user_id" not in sess
