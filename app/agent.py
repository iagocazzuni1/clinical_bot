import os
import json
from openai import OpenAI
from dotenv import load_dotenv

from app.memory import get_historico, salvar_mensagem
from app import tools

load_dotenv()

MOCK_MODE = os.environ.get("MOCK_MODE", "false").lower() == "true"

_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "placeholder"))

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """Você é Sofia, assistente virtual da Clínica Saúde Total.
Seu papel é atender pacientes via WhatsApp com cordialidade e eficiência.

Você pode:
- Agendar consultas médicas
- Cancelar consultas existentes
- Realizar triagem de sintomas e orientar sobre urgência

Regras:
- Sempre se apresente pelo nome na primeira mensagem.
- Colete todas as informações necessárias antes de chamar uma ferramenta.
- Em casos de alta urgência identificados na triagem, reforce a orientação de ligar para o SAMU (192).
- Nunca forneça diagnósticos médicos; apenas oriente sobre o nível de urgência.
- Mantenha um tom empático, claro e profissional."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "agendar_consulta",
            "description": "Agenda uma consulta médica para o paciente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_paciente": {"type": "string", "description": "Nome completo do paciente."},
                    "especialidade": {"type": "string", "description": "Especialidade médica desejada."},
                    "data_hora": {"type": "string", "description": "Data e hora da consulta (ex: 2025-06-10 14:00)."},
                    "telefone": {"type": "string", "description": "Número de telefone do paciente."},
                },
                "required": ["nome_paciente", "especialidade", "data_hora", "telefone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancelar_consulta",
            "description": "Cancela uma consulta previamente agendada.",
            "parameters": {
                "type": "object",
                "properties": {
                    "telefone": {"type": "string", "description": "Número de telefone do paciente."},
                    "motivo": {"type": "string", "description": "Motivo do cancelamento."},
                },
                "required": ["telefone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "triagem_sintomas",
            "description": "Realiza triagem de sintomas e classifica o nível de urgência (BAIXA, MEDIA ou ALTA).",
            "parameters": {
                "type": "object",
                "properties": {
                    "sintomas": {"type": "string", "description": "Descrição dos sintomas relatados pelo paciente."},
                    "duracao": {"type": "string", "description": "Há quanto tempo os sintomas estão presentes."},
                },
                "required": ["sintomas"],
            },
        },
    },
]


def executar_tool(nome: str, inputs: dict) -> str:
    if nome == "agendar_consulta":
        return tools.agendar_consulta(**inputs)
    if nome == "cancelar_consulta":
        return tools.cancelar_consulta(**inputs)
    if nome == "triagem_sintomas":
        return tools.triagem_sintomas(**inputs)
    return f"Ferramenta '{nome}' não reconhecida."


def _processar_mock(telefone: str, mensagem: str) -> str:
    msg = mensagem.lower()
    historico = get_historico(telefone)
    primeira_vez = len(historico) == 0

    if primeira_vez:
        resposta = "Olá! Sou a Sofia, assistente virtual da Clínica Saúde Total. Como posso te ajudar?"
    elif any(p in msg for p in ("agendar", "consulta", "marcar")):
        partes = mensagem.split(",")
        nome = partes[0].strip() if len(partes) > 0 else "Paciente"
        especialidade = partes[1].strip() if len(partes) > 1 else "Clínico Geral"
        data_hora = partes[2].strip() if len(partes) > 2 else "a definir"
        resultado = tools.agendar_consulta(nome, especialidade, data_hora, telefone)
        resposta = f"Perfeito! {resultado}\nQualquer dúvida, estou à disposição."
    elif any(p in msg for p in ("cancelar", "desmarcar", "cancelamento")):
        resultado = tools.cancelar_consulta(telefone, mensagem)
        resposta = f"{resultado}\nLamentamos a sua ausência. Quando quiser reagendar, é só nos chamar!"
    elif any(p in msg for p in ("dor", "febre", "sintoma", "mal", "falta de ar", "peito", "enjoo")):
        resultado = tools.triagem_sintomas(mensagem)
        resposta = f"{resultado}\nSe os sintomas piorarem, não hesite em buscar atendimento."
    else:
        resposta = "Entendido! Posso ajudar com agendamentos, cancelamentos ou orientações sobre sintomas. O que você precisa?"

    historico_novo = historico + [
        {"role": "user", "content": mensagem},
        {"role": "assistant", "content": resposta},
    ]
    salvar_mensagem(telefone, historico_novo)
    return resposta


def processar_mensagem(telefone: str, mensagem: str) -> str:
    if MOCK_MODE:
        return _processar_mock(telefone, mensagem)

    historico = get_historico(telefone)
    historico.append({"role": "user", "content": mensagem})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + historico

    max_iteracoes = 5
    for _ in range(max_iteracoes):
        response = _client.chat.completions.create(
            model=MODEL,
            tools=TOOLS,
            messages=messages,
        )

        choice = response.choices[0]
        assistant_message = choice.message

        messages.append(assistant_message.model_dump(exclude_unset=False))

        if choice.finish_reason in ("stop", "length"):
            historico.append({"role": "assistant", "content": assistant_message.content})
            salvar_mensagem(telefone, historico)
            return assistant_message.content or ""

        for tool_call in (assistant_message.tool_calls or []):
            inputs = json.loads(tool_call.function.arguments)
            resultado = executar_tool(tool_call.function.name, inputs)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": resultado,
            })
