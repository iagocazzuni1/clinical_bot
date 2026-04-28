# Bot de Clínica — Sofia

Assistente virtual para clínicas médicas via WhatsApp. A Sofia atende pacientes, agenda consultas no Google Calendar, cancela agendamentos e realiza triagem de sintomas com classificação de urgência.

---

## Funcionalidades

- **Agendamento de consultas** — coleta nome, especialidade, data/hora e telefone, e cria evento no Google Calendar
- **Cancelamento de consultas** — localiza e cancela o próximo evento do paciente pelo telefone
- **Triagem de sintomas** — classifica urgência em BAIXA, MÉDIA ou ALTA e orienta sobre SAMU em casos graves
- **Histórico de conversa** — mantém contexto por sessão para conversas naturais

---

## Tecnologias

- **Python 3.9+**
- **FastAPI** — servidor web e endpoint de webhook
- **OpenAI GPT-4o-mini** — motor de linguagem da assistente
- **Twilio** — integração com WhatsApp
- **Google Calendar API** — agendamento real de consultas
- **ngrok** — exposição do servidor local para testes

---

## Estrutura do projeto

```
Bot de Clinica/
├── app/
│   ├── agent.py       # Lógica principal da IA (OpenAI + tools)
│   ├── main.py        # Servidor FastAPI e endpoint /webhook
│   ├── memory.py      # Histórico de conversa por telefone (em memória)
│   └── tools.py       # Ferramentas: agendar, cancelar, triagem
├── test_agent.py      # Script de testes das conversas
├── requirements.txt   # Dependências do projeto
├── .env.example       # Exemplo de variáveis de ambiente
└── .gitignore
```

---

## Configuração

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd "Bot de Clinica"
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha com seus dados:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
OPENAI_API_KEY=sua-chave-openai
MOCK_MODE=false
TWILIO_ACCOUNT_SID=seu-account-sid
TWILIO_AUTH_TOKEN=seu-auth-token
TWILIO_WHATSAPP_NUMBER=+14155238886
```

### 4. Configurar Google Calendar (opcional)

Para agendamento real no Google Calendar:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto e ative a **Google Calendar API**
3. Crie credenciais OAuth 2.0 e baixe o arquivo como `credentials.json` na raiz do projeto
4. Na primeira execução, um navegador abrirá para autorização — isso gera o `token.json` automaticamente

Se `credentials.json` não estiver presente, o bot responde com uma mensagem de erro amigável ao tentar agendar.

---

## Rodando o projeto

### Modo de teste (sem chamadas à OpenAI)

```env
MOCK_MODE=true
```

```bash
python test_agent.py
```

### Servidor real

**Terminal 1 — Subir o servidor:**

```bash
# Windows (Anaconda)
& "C:\Users\SeuUsuario\anaconda3\python.exe" -m uvicorn app.main:app --reload --port 8080
```

**Terminal 2 — Expor com ngrok:**

```bash
ngrok http 8080
```

Copie a URL gerada (ex: `https://abc123.ngrok-free.app`).

---

## Configurando o Twilio

1. Acesse o [Twilio Console](https://console.twilio.com)
2. Vá em **Messaging → Try it out → Send a WhatsApp message**
3. Em **Sandbox Settings**, preencha:
   - **When a message comes in:** `https://abc123.ngrok-free.app/webhook`
   - Método: `HTTP POST`
4. Salve as configurações

### Ativar o Sandbox

No seu WhatsApp, envie para o número do sandbox (`+14155238886`):

```
join <palavra-chave-do-sandbox>
```

A palavra-chave aparece no painel do Twilio (ex: `join sandy-tiger`).

Após isso, basta mandar **"Oi"** e a Sofia responde.

---

## Adaptando para um cliente

Para instalar o bot para um novo cliente, atualize no `.env`:

| Variável | O que mudar |
|---|---|
| `OPENAI_API_KEY` | Chave da OpenAI do cliente |
| `TWILIO_ACCOUNT_SID` | SID da conta Twilio do cliente |
| `TWILIO_AUTH_TOKEN` | Token da conta Twilio do cliente |
| `TWILIO_WHATSAPP_NUMBER` | Número WhatsApp aprovado do cliente |

E em `app/agent.py`, atualize o `SYSTEM_PROMPT` com o nome da assistente e da clínica.

Para produção, substitua o ngrok por um servidor real (VPS, Railway, Render, etc.).

---

## Variáveis de ambiente

| Variável | Descrição | Obrigatório |
|---|---|---|
| `OPENAI_API_KEY` | Chave de API da OpenAI | Sim |
| `MOCK_MODE` | `true` para testes sem IA | Não (padrão: `false`) |
| `TWILIO_ACCOUNT_SID` | SID da conta Twilio | Sim |
| `TWILIO_AUTH_TOKEN` | Token de autenticação Twilio | Sim |
| `TWILIO_WHATSAPP_NUMBER` | Número WhatsApp do Twilio | Sim |
