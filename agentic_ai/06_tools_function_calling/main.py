from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import yaml
import json

RAIZ = Path(__file__).resolve().parents[1]


def conectar(nome=None):
    ambiente = dotenv_values(RAIZ / ".env")
    chave = ambiente.get("OPENAI_API_KEY", "")
    perfis = yaml.safe_load((RAIZ / "config/models.yaml").read_text(encoding="utf-8"))
    perfil = perfis[nome or ambiente.get("PERFIL_MODELO", "fast")]
    cliente = OpenAI(api_key=chave, timeout=30, max_retries=0)
    parametros = {
        "model": perfil["model"],
        "reasoning": {"effort": perfil["reasoning_effort"]},
        "max_output_tokens": 1200,
        "store": False,
    }
    return cliente, parametros


FERRAMENTAS = [
    {
        "type": "function",
        "name": "consultar_matricula",
        "description": "Consulta o status de uma matrícula pelo código, como M001.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {"matricula": {"type": "string"}},
            "required": ["matricula"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "consultar_curso",
        "description": (
            "Consulta a duração de um curso pelo nome, como Python ou Dados."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {"curso": {"type": "string"}},
            "required": ["curso"],
            "additionalProperties": False,
        },
    },
]


def consultar_matricula(matricula):
    return {
        "status": {"M001": "ativa", "M002": "cancelada"}.get(
            matricula, "não encontrada"
        )
    }


def consultar_curso(curso):
    return {"duracao_horas": "20"}


def main():
    cliente, parametros = conectar()
    historico = [
        {
            "role": "user",
            "content": (
                "Quanto dura o curso de Python e qual é a situação da matrícula M001?"
            ),
        }
    ]
    for _ in range(3):
        resposta = cliente.responses.create(
            **parametros, input=historico, tools=FERRAMENTAS
        )
        historico.extend(resposta.output)
        chamadas = [item for item in resposta.output if item.type == "function_call"]
        if not chamadas:
            print(resposta.output_text)
            return
        else:
            print(
                "LLM executado. Ferramentas solicitadas:",
                ", ".join(chamada.name for chamada in chamadas),
            )
        for chamada in chamadas:
            argumentos = json.loads(chamada.arguments)
            if chamada.name == "consultar_matricula":
                resultado = consultar_matricula(**argumentos)
            elif chamada.name == "consultar_curso":
                resultado = consultar_curso(**argumentos)

            print("Ferramenta:", chamada.name, "| Observação:", resultado)
            historico.append(
                {
                    "type": "function_call_output",
                    "call_id": chamada.call_id,
                    "output": json.dumps(resultado),
                }
            )
    print("Limite de três rodadas atingido.")


if __name__ == "__main__":
    main()
