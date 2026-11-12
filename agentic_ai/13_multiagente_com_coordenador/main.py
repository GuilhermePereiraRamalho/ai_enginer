from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import yaml

RAIZ = Path(__file__).resolve().parents[1]
POLITICA = (
    "Política fictícia: pedidos em até 7 dias da matrícula podem ser "
    "analisados para reembolso. Todo reembolso exige aprovação humana. "
    "Após 7 dias, encaminhe a exceção para análise da equipe."
)

FERRAMENTAS = [
    {
        "type": "function",
        "name": "chamar_triagem",
        "description": (
            "Pede os dados ausentes quando faltam matrícula ou dias desde a matrícula."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "chamar_especialista",
        "description": (
            "Analisa cancelamento quando matrícula e dias desde a matrícula estão "
            "informados."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
]


def conectar():
    ambiente = dotenv_values(RAIZ / ".env")
    perfis = yaml.safe_load((RAIZ / "config/models.yaml").read_text(encoding="utf-8"))
    perfil = perfis[ambiente.get("PERFIL_MODELO", "fast")]
    cliente = OpenAI(
        api_key=ambiente.get("OPENAI_API_KEY", ""), timeout=30, max_retries=0
    )
    parametros = {
        "model": perfil["model"],
        "reasoning": {"effort": perfil["reasoning_effort"]},
        "max_output_tokens": 1200,
        "store": False,
    }
    return cliente, parametros


def chamar_triagem(cliente, parametros, pedido):
    resposta = cliente.responses.create(
        **parametros,
        instructions=(
            "Você é o agente de triagem de cancelamento. Responda em português, "
            "pedindo somente os dados que faltam: matrícula e dias desde a matrícula. "
            "Não invente dados nem decida sobre reembolso. Seja breve."
        ),
        input=pedido
    )
    return resposta.output_text


def chamar_especialista(cliente, parametros, pedido):
    resposta = cliente.responses.create(
        **parametros,
        instructions=(
            "Você é o especialista em cancelamento. Responda em português, "
            "de forma breve, aplicando esta política: "
            + POLITICA
            + " Os dados são declarados pelo aluno, não verificados. "
            "Se faltar informação, peça-a. Não afirme ter cancelado ou pago nada."
        ),
        input=pedido
    )
    return resposta.output_text


def agente_coordenador(cliente, parametros, pedido):
    resposta = cliente.responses.create(
        **parametros,
        instructions=(
            "Você coordena o atendimento de cancelamento. "
            "Escolha triagem quando faltar matrícula ou dias desde a matrícula. "
            "Escolha especialista quando ambos estiverem informados."
        ),
        input=pedido,
        tools=FERRAMENTAS,
        tool_choice="required",
        parallel_tool_calls=False
    )
    chamada = next(item for item in resposta.output if item.type == "function_call")
    print("Coordenador escolheu:", chamada.name)
    if chamada.name == "chamar_triagem":
        return chamar_triagem(cliente, parametros, pedido)
    if chamada.name == "chamar_especialista":
        return chamar_especialista(cliente, parametros, pedido)
    raise ValueError("Agente não permitido.")


def main():
    cliente, parametros = conectar()
    for pedido in [
        "Quero cancelar meu curso.",
        "Quero cancelar a matrícula M001, feita há 3 dias.",
    ]:
        print("\nPedido do aluno:", pedido)
        resposta = agente_coordenador(cliente, parametros, pedido)
        print("Resposta:", resposta)


if __name__ == "__main__":
    main()
