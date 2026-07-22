"""Rotas da agenda medica. As rotas nao fazem requests: delegam ao ApiService."""
from flask import Blueprint, jsonify, render_template

from app.blueprints.auth.decorators import login_required
from app.services.api_service import ApiService

agenda_bp = Blueprint("agenda", __name__)
_api_service = ApiService()


@agenda_bp.route("/agenda")
@login_required
def agenda():
    # Placeholder: a tabela (Tabulator) sera implementada na etapa 6.
    return render_template("agenda.html")


@agenda_bp.get("/api/agendamentos")
@login_required
def api_agendamentos():
    resultado = _api_service.listar_agendamentos()
    return jsonify(
        {
            "agendamentos": [a.to_dict() for a in resultado.agendamentos],
            "aviso": resultado.aviso,
        }
    )
