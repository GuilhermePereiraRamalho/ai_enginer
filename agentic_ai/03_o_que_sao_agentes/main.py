import json
from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import yaml

RAIZ = Path(__file__).resolve().parents[1]

FERRAMENTA = {
    "type": "function",
    "name": "consultar_matricula",
    "description": "Consulta o status de uma matrícula da escola.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {"codigo": {"type": "string"}},
        "required": ["codigo"],
        "additionalProperties": False,
    },
}


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


def consultar_matricula(codigo):
    return {"M001": "ativa"}.get(codigo, "não encontrada")


def main():
    pergunta = "Qual é a situação da minha matrícula M001?"
    cliente, parametros = conectar()
    instrucoes = (
        "Responda em português. Para informar o status de uma matrícula, "
        "consulte a ferramenta. Se faltar o código, peça-o. Não invente dados."
    )
    historico = [{"role": "user", "content": pergunta}]
    resposta = cliente.responses.create(
        **parametros,
        instructions=instrucoes,
        input=historico,
        tools=[FERRAMENTA],
        parallel_tool_calls=False
    )
    chamadas = [item for item in resposta.output if item.type == "function_call"]
    if chamadas:
        historico.extend(resposta.output)
        for chamada in chamadas:
            argumentos = json.loads(chamada.arguments)
            print("Ferramenta solicitada pelo modelo:", chamada.name)
            print("Argumentos:", argumentos)
            observacao = consultar_matricula(**argumentos)
            print("Resultado da ferramenta:", observacao)
            historico.append(
                {
                    "type": "function_call_output",
                    "call_id": chamada.call_id,
                    "output": observacao,
                }
            )
        resposta = cliente.responses.create(
            **parametros, instructions=instrucoes, input=historico
        )
    print("Resposta:", resposta.output_text)


if __name__ == "__main__":
    main()
