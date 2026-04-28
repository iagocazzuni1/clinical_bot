import os
import datetime
from zoneinfo import ZoneInfo

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_SCOPES = ["https://www.googleapis.com/auth/calendar"]
_TIMEZONE = "America/Sao_Paulo"
_CALENDAR_ID = "primary"

_ALTA_URGENCIA = {"dor no peito", "falta de ar", "desmaio", "sangramento intenso"}
_MEDIA_URGENCIA = {"febre alta", "vômito", "dor intensa"}


def _get_calendar_service():
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError(
            "credentials.json não encontrado. Consulte o README para configurar o Google Calendar."
        )

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", _SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", _SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def agendar_consulta(
    nome_paciente: str,
    especialidade: str,
    data_hora: str,
    telefone: str,
) -> str:
    try:
        service = _get_calendar_service()
    except FileNotFoundError as e:
        return str(e)

    tz = ZoneInfo(_TIMEZONE)
    inicio = datetime.datetime.strptime(data_hora, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
    fim = inicio + datetime.timedelta(minutes=30)

    evento = {
        "summary": f"Consulta - {especialidade} - {nome_paciente}",
        "description": f"Agendado via WhatsApp. Telefone: {telefone}",
        "start": {"dateTime": inicio.isoformat(), "timeZone": _TIMEZONE},
        "end": {"dateTime": fim.isoformat(), "timeZone": _TIMEZONE},
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24 * 60},
                {"method": "popup", "minutes": 30},
            ],
        },
    }

    resultado = service.events().insert(calendarId=_CALENDAR_ID, body=evento).execute()
    link = resultado.get("htmlLink", "")
    data_fmt = inicio.strftime("%d/%m/%Y às %H:%M")

    return (
        f"Consulta agendada com sucesso!\n"
        f"Paciente: {nome_paciente}\n"
        f"Especialidade: {especialidade}\n"
        f"Data/Hora: {data_fmt}\n"
        f"Telefone: {telefone}\n"
        f"Link: {link}"
    )


def cancelar_consulta(telefone: str, motivo: str = "não informado") -> str:
    try:
        service = _get_calendar_service()
    except FileNotFoundError as e:
        return str(e)

    agora = datetime.datetime.utcnow().isoformat() + "Z"
    eventos = (
        service.events()
        .list(
            calendarId=_CALENDAR_ID,
            timeMin=agora,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
            q=telefone,
        )
        .execute()
    )

    items = eventos.get("items", [])
    if not items:
        return f"Nenhuma consulta futura encontrada para o telefone {telefone}."

    evento = items[0]
    service.events().delete(calendarId=_CALENDAR_ID, eventId=evento["id"]).execute()

    summary = evento.get("summary", "Consulta")
    start = evento.get("start", {}).get("dateTime", "")
    if start:
        dt = datetime.datetime.fromisoformat(start)
        data_fmt = dt.strftime("%d/%m/%Y às %H:%M")
    else:
        data_fmt = "data não definida"

    return (
        f"Consulta cancelada com sucesso!\n"
        f"Evento: {summary}\n"
        f"Data/Hora: {data_fmt}\n"
        f"Motivo: {motivo}"
    )


def triagem_sintomas(sintomas: str, duracao: str = "não informado") -> str:
    sintomas_lower = sintomas.lower()

    if any(kw in sintomas_lower for kw in _ALTA_URGENCIA):
        urgencia = "ALTA"
    elif any(kw in sintomas_lower for kw in _MEDIA_URGENCIA):
        urgencia = "MEDIA"
    else:
        urgencia = "BAIXA"

    resposta = (
        f"Triagem realizada.\n"
        f"Sintomas relatados: {sintomas}\n"
        f"Duração: {duracao}\n"
        f"Urgência classificada: {urgencia}"
    )

    if urgencia == "ALTA":
        resposta += "\n\n⚠️ Ligue imediatamente para o SAMU: 192"

    return resposta
