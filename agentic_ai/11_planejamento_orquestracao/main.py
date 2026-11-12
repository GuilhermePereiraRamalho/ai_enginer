def planejar(matricula, aprovado=False):
    if not matricula:
        return ["receber pedido", "pedir matrícula"]
    dias = {"M001": 3, "M002": 12}[matricula]
    passos = ["consultar matrícula", "verificar política"]
    if dias > 7:
        return passos + ["encaminhar exceção à equipe"]
    if not aprovado:
        return passos + ["pausar para aprovação humana"]
    return passos + ["registrar conclusão simulada"]


def main():
    for matricula, aprovado in [
        (None, False),
        ("M001", False),
        ("M001", True),
        ("M002", False),
    ]:
        print(
            matricula,
            "| aprovado:",
            aprovado,
            "| fluxo:",
            planejar(matricula, aprovado),
        )


if __name__ == "__main__":
    main()
