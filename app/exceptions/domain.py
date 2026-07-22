"""Excecoes de dominio tipadas (base do tratamento da Parte 2)."""


class DomainError(Exception):
    """Base de todas as excecoes de dominio."""


class CredenciaisInvalidasError(DomainError):
    """Usuario nao encontrado ou senha incorreta."""


class ApiIndisponivelError(DomainError):
    """API de agendamentos inacessivel (timeout, conexao ou 5xx)."""


class ApiRespostaInvalidaError(DomainError):
    """Resposta da API fora do contrato (JSON invalido ou formato inesperado)."""


class CampoObrigatorioAusenteError(DomainError):
    """Registro sem um ou mais campos obrigatorios."""

    def __init__(self, campos) -> None:
        self.campos = list(campos)
        super().__init__("Campos obrigatorios ausentes: " + ", ".join(self.campos))


class BancoIndisponivelError(DomainError):
    """Falha de conexao ou acesso ao banco de dados."""
