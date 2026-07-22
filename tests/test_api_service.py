"""Testes do ApiService (integracao HTTP com a API de agendamentos)."""
import requests

from app.services.api_service import ApiService

_REGISTRO = {
    "paciente": "Maria Silva",
    "cpf": "123.456.789-00",
    "medico": "Dr. Joao Souza",
    "especialidade": "Cardiologia",
    "data": "2026-07-24",
    "horario": "09:00",
    "convenio": "Unimed",
    "status": "Confirmado",
}


class _FakeResp:
    def __init__(self, status=200, payload=None, json_invalido=False):
        self.status_code = status
        self._payload = payload
        self._json_invalido = json_invalido

    def json(self):
        if self._json_invalido:
            raise ValueError("json invalido")
        return self._payload


class _FakeSession:
    def __init__(self, resp=None, exc=None):
        self._resp = resp
        self._exc = exc

    def get(self, url, timeout=None):
        if self._exc:
            raise self._exc
        return self._resp


def _svc(session):
    return ApiService(base_url="http://api", timeout=1, session=session)


def test_sucesso_retorna_agendamentos():
    r = _svc(_FakeSession(_FakeResp(200, [_REGISTRO]))).listar_agendamentos()
    assert len(r.agendamentos) == 1
    assert r.aviso is None


def test_timeout_faz_fallback():
    r = _svc(_FakeSession(exc=requests.Timeout())).listar_agendamentos()
    assert r.agendamentos == []
    assert r.aviso


def test_conexao_faz_fallback():
    r = _svc(_FakeSession(exc=requests.ConnectionError())).listar_agendamentos()
    assert r.agendamentos == []
    assert r.aviso


def test_json_invalido_faz_fallback():
    r = _svc(_FakeSession(_FakeResp(200, json_invalido=True))).listar_agendamentos()
    assert r.agendamentos == []
    assert r.aviso


def test_formato_inesperado_faz_fallback():
    r = _svc(_FakeSession(_FakeResp(200, {"x": 1}))).listar_agendamentos()
    assert r.agendamentos == []
    assert r.aviso


def test_status_503_faz_fallback():
    r = _svc(_FakeSession(_FakeResp(503, {"erro": "x"}))).listar_agendamentos()
    assert r.agendamentos == []
    assert r.aviso


def test_campos_faltando_ignora_registro():
    incompleto = {"paciente": "Sem resto"}
    r = _svc(_FakeSession(_FakeResp(200, [_REGISTRO, incompleto]))).listar_agendamentos()
    assert len(r.agendamentos) == 1
    assert r.aviso  # avisa que houve registro ignorado
