"""Agendamento: representacao validada de um registro vindo da API.

Nao e persistido (vem da API), por isso e um dataclass simples e nao um
modelo SQLAlchemy.
"""
from dataclasses import asdict, dataclass

from app.exceptions.domain import CampoObrigatorioAusenteError

CAMPOS_OBRIGATORIOS = (
    "paciente",
    "cpf",
    "medico",
    "especialidade",
    "data",
    "horario",
    "convenio",
    "status",
)


@dataclass(frozen=True)
class Agendamento:
    paciente: str
    cpf: str
    medico: str
    especialidade: str
    data: str
    horario: str
    convenio: str
    status: str

    @classmethod
    def from_dict(cls, raw: dict) -> "Agendamento":
        """Cria um Agendamento validando os campos obrigatorios.

        Levanta CampoObrigatorioAusenteError quando algum campo obrigatorio
        esta ausente ou vazio.
        """
        faltando = [campo for campo in CAMPOS_OBRIGATORIOS if not raw.get(campo)]
        if faltando:
            raise CampoObrigatorioAusenteError(faltando)
        return cls(**{campo: raw[campo] for campo in CAMPOS_OBRIGATORIOS})

    def to_dict(self) -> dict:
        return asdict(self)
