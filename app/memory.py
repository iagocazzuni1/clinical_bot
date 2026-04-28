_historicos: dict[str, list[dict]] = {}

MAX_MENSAGENS = 20


def get_historico(telefone: str) -> list[dict]:
    return _historicos.get(telefone, [])


def salvar_mensagem(telefone: str, historico: list[dict]) -> None:
    _historicos[telefone] = historico[-MAX_MENSAGENS:]
