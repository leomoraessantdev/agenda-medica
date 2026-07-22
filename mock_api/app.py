"""Microservico HTTP que simula a API de agendamentos.

A rota apenas orquestra e nao contem dados. Toda a logica (inclusive os
cenarios de falha) fica na camada de service.
"""
import os

from flask import Flask, jsonify, request

from scenarios import Scenario
from services.agendamento_service import AgendamentoService


def create_app() -> Flask:
    app = Flask(__name__)
    service = AgendamentoService()

    @app.get("/")
    def index():
        return jsonify(
            {
                "servico": "mock-agendamentos",
                "endpoints": {
                    "health": "/health",
                    "agendamentos": "/agendamentos?cenario=ok|vazio|invalido|campos_faltando|indisponivel",
                },
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/agendamentos")
    def agendamentos():
        # Cenario vem da query (?cenario=) ou da env MOCK_SCENARIO.
        cenario = Scenario.normalizar(
            request.args.get("cenario") or os.getenv("MOCK_SCENARIO")
        )
        payload, status = service.obter(cenario)
        return jsonify(payload), status

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
