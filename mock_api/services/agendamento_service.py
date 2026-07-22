"""Camada de service do microservico: monta a resposta conforme o cenario.

Os dados vem de data/agendamentos.json, nunca hardcoded na rota.
"""
import json
from pathlib import Path

from scenarios import Scenario

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "agendamentos.json"


class AgendamentoService:
    def __init__(self, data_file: Path = _DATA_FILE) -> None:
        self._data_file = data_file

    def _carregar(self) -> list[dict]:
        with self._data_file.open(encoding="utf-8") as fh:
            return json.load(fh)

    def obter(self, cenario: str) -> tuple[object, int]:
        """Devolve (payload, status_code) conforme o cenario simulado."""
        if cenario == Scenario.INDISPONIVEL:
            return {"erro": "Servico temporariamente indisponivel"}, 503
        if cenario == Scenario.VAZIO:
            return [], 200
        if cenario == Scenario.INVALIDO:
            # JSON valido, porem fora do contrato (objeto no lugar de lista).
            return {"mensagem": "resposta fora do contrato esperado"}, 200
        if cenario == Scenario.CAMPOS_FALTANDO:
            return self._sem_campos_obrigatorios(), 200
        return self._carregar(), 200

    def _sem_campos_obrigatorios(self) -> list[dict]:
        registros = self._carregar()
        incompletos = []
        for indice, registro in enumerate(registros):
            copia = dict(registro)
            if indice == 0:
                copia.pop("cpf", None)
            elif indice == 1:
                copia.pop("convenio", None)
                copia.pop("status", None)
            incompletos.append(copia)
        return incompletos
