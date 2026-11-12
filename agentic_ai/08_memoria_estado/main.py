import sqlite3
from pathlib import Path


def main():
    pasta = Path(__file__).parent / "saida"
    pasta.mkdir(exist_ok=True)
    with sqlite3.connect(pasta / "memoria.sqlite3") as banco:
        banco.execute(
            "CREATE TABLE IF NOT EXISTS atendimento (id INTEGER PRIMARY KEY, curso "
            "TEXT, estado TEXT)"
        )
        print("Turno 1: tenho interesse em Python.")
        banco.execute(
            "INSERT OR REPLACE INTO atendimento VALUES (1, 'Python', 'aguardando_vaga')"
        )
    with sqlite3.connect(pasta / "memoria.sqlite3") as banco:
        curso, estado = banco.execute(
            "SELECT curso, estado FROM atendimento WHERE id=1"
        ).fetchone()
    print("Turno 2: qual curso eu mencionei? Resposta:", curso)
    print("Estado da tarefa:", estado)


if __name__ == "__main__":
    main()
