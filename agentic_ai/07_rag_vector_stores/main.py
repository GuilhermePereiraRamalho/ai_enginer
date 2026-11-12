from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import yaml
import json
import faiss
import numpy as np

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


def vetorizar(cliente, textos):
    print("\nEnviando", len(textos), "texto(s) para text-embedding-3-small:")
    resposta = cliente.embeddings.create(model="text-embedding-3-small", input=textos)
    vetores = np.array(
        [item.embedding for item in sorted(resposta.data, key=lambda item: item.index)],
        dtype="float32",
    )
    print(
        f"Matriz recebida: {vetores.shape[0]} vetores x {vetores.shape[1]} dimensões;"
        f" tipo: {vetores.dtype}"
    )
    print("Primeiras 5 coordenadas de cada vetor (antes da normalização):")
    print(np.round(vetores[:, :5], 4))
    return vetores


def main():
    documentos = json.loads(
        Path(__file__).with_name("politicas.json").read_text(encoding="utf-8")
    )
    pergunta = "Qual a política de cancelamento e reembolso?"
    cliente, parametros = conectar()
    vetores = vetorizar(cliente, [documento["texto"] for documento in documentos])
    indice = faiss.IndexFlatIP(vetores.shape[1])
    indice.add(vetores)
    consulta = vetorizar(cliente, [pergunta])
    similaridades, posicoes = indice.search(consulta, k=1)
    trecho = documentos[int(posicoes[0][0])]
    print("Vetores no índice FAISS:", indice.ntotal)
    print("Similaridade:", round(float(similaridades[0][0]), 3))
    print("Trecho recuperado:", trecho)
    resposta = cliente.responses.create(
        **parametros,
        instructions=(
            "Responda somente com base no trecho e cite seu ID. Admita lacunas."
        ),
        input=f"Trecho [{trecho['id']}]: {trecho['texto']}\nPergunta: {pergunta}",
    )
    print(resposta.output_text)


if __name__ == "__main__":
    main()
