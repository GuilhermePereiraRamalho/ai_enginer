from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import yaml

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


FERRAMENTA = {
    "type": "function",
    "name": "carregar_cancelamento",
    "description": "Carrega a skill para orientar cancelamento de matrícula.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
}

INSTRUCOES = (
    "Você atende uma escola fictícia. Responda em português e seja breve. "
    "Se uma skill for relevante, carregue-a antes de orientar o aluno. "
    "Siga o procedimento carregado. Não invente cursos, consultas ou ações realizadas."
)


def carregar_cancelamento():
    return (Path(__file__).parent / "skills/cancelamento.md").read_text(
        encoding="utf-8"
    )


def main():
    cliente, parametros = conectar()
    print("Skill disponível:", FERRAMENTA["description"])
    for pedido in ["Quais cursos existem?", "Quero encerrar meu vínculo com a escola."]:
        print("\nPedido:", pedido)
        historico = [{"role": "user", "content": pedido}]
        resposta = cliente.responses.create(
            **parametros,
            instructions=INSTRUCOES,
            input=historico,
            tools=[FERRAMENTA],
            parallel_tool_calls=False
        )
        chamadas = [item for item in resposta.output if item.type == "function_call"]
        if chamadas:
            historico.extend(resposta.output)
            for chamada in chamadas:
                procedimento = carregar_cancelamento()
                print("Skill carregada: cancelamento")
                historico.append(
                    {
                        "type": "function_call_output",
                        "call_id": chamada.call_id,
                        "output": procedimento,
                    }
                )
            resposta = cliente.responses.create(
                **parametros, instructions=INSTRUCOES, input=historico
            )
        else:
            print("Nenhuma skill carregada.")
        print("Resposta:", resposta.output_text)


if __name__ == "__main__":
    main()
