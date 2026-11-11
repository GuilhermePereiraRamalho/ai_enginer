from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import yaml
import time

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
    perfis = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "config/models.yaml").read_text(
            encoding="utf-8"
        )
    )
    pergunta = "Uma matrícula de 3 dias pode receber reembolso automaticamente?"
    for nome, perfil in perfis.items():
        print("\nPerfil:", nome, "| Esforço:", perfil["reasoning_effort"])
        print(
            "USD/1M entrada/saída:",
            perfil["input_usd_million"],
            perfil["output_usd_million"],
        )
        cliente, parametros = conectar(nome)
        inicio = time.perf_counter()
        resposta = cliente.responses.create(
            **parametros,
            input=pergunta,
            instructions=(
                "Política fictícia: até 7 dias permite análise; aprovação humana é "
                "obrigatória."
            ),
        )
        print("Resposta:", resposta.output_text)
        print("Segundos:", round(time.perf_counter() - inicio, 3))
        print(
            "Tokens entrada/saída:",
            resposta.usage.input_tokens,
            resposta.usage.output_tokens,
        )
        custo = (
            resposta.usage.input_tokens * perfil["input_usd_million"]
            + resposta.usage.output_tokens * perfil["output_usd_million"]
        ) / 1_000_000
        print("Custo estimado USD:", custo)


if __name__ == "__main__":
    main()
