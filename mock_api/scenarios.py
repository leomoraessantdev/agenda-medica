"""Cenarios simulaveis pela API mock (selecionados por ?cenario= ou MOCK_SCENARIO)."""


class Scenario:
    OK = "ok"
    VAZIO = "vazio"
    INVALIDO = "invalido"
    CAMPOS_FALTANDO = "campos_faltando"
    INDISPONIVEL = "indisponivel"

    _VALIDOS = {OK, VAZIO, INVALIDO, CAMPOS_FALTANDO, INDISPONIVEL}

    @classmethod
    def normalizar(cls, valor: str | None, padrao: str = OK) -> str:
        candidato = (valor or padrao).strip().lower()
        return candidato if candidato in cls._VALIDOS else padrao
