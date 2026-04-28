import logging

from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse

from app.agent import processar_mensagem

logger = logging.getLogger("clinica_bot")

app = FastAPI(title="Clinica Bot")

_TWIML_ERRO = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<Response>"
    "<Message>Desculpe, ocorreu um erro interno. Tente novamente em instantes.</Message>"
    "</Response>"
)


def _twiml(mensagem: str) -> PlainTextResponse:
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response>"
        f"<Message>{mensagem}</Message>"
        "</Response>"
    )
    return PlainTextResponse(content=body, media_type="text/xml")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(From: str = Form(...), Body: str = Form(...)):
    telefone = From.replace("whatsapp:", "")
    try:
        resposta = processar_mensagem(telefone, Body)
        return _twiml(resposta)
    except Exception:
        logger.exception("Erro ao processar mensagem de %s", telefone)
        return PlainTextResponse(content=_TWIML_ERRO, media_type="text/xml", status_code=200)
