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


def montar_contexto(blocos, limite):
    contexto = ""
    for nome, conteudo in blocos:
        bloco = f"[{nome}]\n{conteudo}\n"
        if len(contexto + bloco) <= limite:
            contexto += bloco
        else:
            print("Descartado por falta de espaço:", nome)
    return contexto


def main():
    blocos = [
        ("memoria", "O aluno quer cancelar."),
        ("documento recuperado", "[P1] Até 7 dias permite análise de reembolso."),
        ("resultado de ferramenta", "M001: matrícula ativa há 3 dias."),
        ("historico antigo", "Mensagem sem relevância. " * 30),
    ]
    contexto = montar_contexto(blocos, limite=350)
    print("\nContexto pronto para enviar ao modelo:\n" + contexto)
    print("Caracteres:", len(contexto), "/ 350 (caracteres não são tokens)")
    cliente, parametros = conectar()
    resposta = cliente.responses.create(
        **parametros,
        instructions=(
            "Responda em português, usando apenas os dados fornecidos. "
            "Reembolsos precisam de aprovação humana. Se faltar informação, peça-a."
        ),
        input=f"Contexto:\n{contexto}\nPedido: Posso receber meu reembolso agora?",
    )
    print("Resposta:", resposta.output_text)


if __name__ == "__main__":
    main()
