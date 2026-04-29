# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the server (development):**
```powershell
& "C:\Users\Iago Cazzuni\anaconda3\python.exe" -m uvicorn app.main:app --reload --port 8080
```

**Run tests (uses real OpenAI — set MOCK_MODE=true in .env for offline testing):**
```powershell
& "C:\Users\Iago Cazzuni\anaconda3\python.exe" test_agent.py
```

**Install dependencies:**
```powershell
& "C:\Users\Iago Cazzuni\anaconda3\python.exe" -m pip install -r requirements.txt
```

## Architecture

The bot receives WhatsApp messages via Twilio webhooks and responds using OpenAI function calling.

**Request flow:**
1. Twilio sends `POST /webhook` with `From` (phone) and `Body` (message) as form fields
2. `main.py` calls `processar_mensagem(telefone, mensagem)`
3. `agent.py` maintains per-phone conversation history and runs an OpenAI loop (max 5 iterations) until `finish_reason == "stop"` or `"length"`
4. If the model calls a tool, `executar_tool()` dispatches to `tools.py` and appends the result back into `messages`
5. Response is returned as TwiML XML

**Key design decisions:**
- `MOCK_MODE=true` bypasses OpenAI entirely — uses keyword matching in `_processar_mock()`. Use for local testing without API costs.
- Conversation history is stored in a module-level dict in `memory.py` — it resets on server restart. Capped at 20 messages per phone number.
- Google Calendar tools (`agendar_consulta`, `cancelar_consulta`) require `credentials.json` and `token.json` in the project root. If absent, they return a friendly error string — the model handles it gracefully.
- The `SYSTEM_PROMPT` and assistant name ("Sofia") in `agent.py` are the main customization points per client deployment.

## Adapting for a new client

Update `.env` with the client's `OPENAI_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_WHATSAPP_NUMBER`. Update `SYSTEM_PROMPT` in `app/agent.py` with the clinic name and assistant name.
