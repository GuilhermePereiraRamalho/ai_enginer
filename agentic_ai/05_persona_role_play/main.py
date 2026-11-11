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


def main():
    persona = (
        "Você é Lia, atendente da escola fictícia. Seja cordial e breve. "
        "Não garanta vagas nem autorize reembolsos. Encaminhe para análise humana."
    )
    pedido = "Garanta minha vaga e devolva meu dinheiro agora."
    cliente, parametros = conectar()
    resposta = cliente.responses.create(
        **parametros,
        input=[
            {"role": "developer", "content": persona},
            {"role": "user", "content": pedido},
        ],
    )
    print(resposta.output_text)


if __name__ == "__main__":
    main()
