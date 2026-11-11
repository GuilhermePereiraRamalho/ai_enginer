from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import yaml

RAIZ = Path(__file__).resolve().parents[1]


def conectar(nome=None):
    ambiente = dotenv_values(RAIZ / ".env")
    chave = ambiente.get("OPENAI_API_KEY", "")
    if not chave or chave.startswith("COLOQUE_"):
        raise SystemExit(
            "Configure OPENAI_API_KEY no .env da raiz para executar este laboratório."
        )
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
    instrucoes = "Use apenas o catálogo fornecido. Admita informações ausentes."
    pergunta = "Quanto dura Python e qual é o preço?"
    contexto = "Catálogo fictício: Python tem 20 horas. Preço não informado."
    cliente, parametros = conectar()
    resposta = cliente.responses.create(
        **parametros,
        instructions=instrucoes,
        input=[{"role": "user", "content": contexto + "\nPergunta: " + pergunta}]
    )
    print(resposta.output_text)


if __name__ == "__main__":
    main()
