import os
import sys
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key or api_key == "sua-chave-aqui":
    print("AVISO: OPENAI_API_KEY não configurada.")
    print("Edite o arquivo .env e substitua pelo valor correto.")
    sys.exit(1)

from app.agent import processar_mensagem

CONVERSAS = [
    {
        "descricao": "Conversa 1 — Agendamento completo",
        "telefone": "+5554991110001",
        "mensagens": [
            "Oi",
            "Quero agendar uma consulta",
            "João Silva, clínico geral, amanhã às 14h",
        ],
    },
    {
        "descricao": "Conversa 2 — Cancelamento",
        "telefone": "+5554991110002",
        "mensagens": [
            "Preciso cancelar minha consulta",
            "Não vou conseguir comparecer",
        ],
    },
    {
        "descricao": "Conversa 3 — Triagem de baixa urgência",
        "telefone": "+5554991110003",
        "mensagens": [
            "Estou com dor de cabeça leve há 2 dias, o que faço?",
        ],
    },
    {
        "descricao": "Conversa 4 — Triagem de alta urgência",
        "telefone": "+5554991110004",
        "mensagens": [
            "Estou sentindo dor no peito e falta de ar",
        ],
    },
]

SEPARADOR = "=" * 60

for conversa in CONVERSAS:
    print(f"\n{SEPARADOR}")
    print(conversa["descricao"])
    print(SEPARADOR)

    telefone = conversa["telefone"]
    for mensagem in conversa["mensagens"]:
        print(f"\n[{telefone}] Paciente: {mensagem}")
        resposta = processar_mensagem(telefone, mensagem)
        print(f"[{telefone}] Sofia: {resposta}")

print(f"\n{SEPARADOR}")
print("Todos os testes concluídos.")
print(SEPARADOR)
