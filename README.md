# 🤖 Support Agent System Utilizing the OpenAI Agents SDK
---


A multi-agent console support system built using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) and Gemini API (`gemini-2.5-flash`). This system routes user queries to specialized agents (billing, technical, general) with dynamic tools, handoffs, output guardrails, and live streaming interactions.


---
## 🧠 Project Objective
---


Build a responsive, intelligent support system that leverages:

- ✅ **Multi-agent collaboration** to resolve diverse support queries
- ✅ **Intelligent triage and routing** via the Triage Agent
- ✅ **Dynamic tool execution** based on user context (e.g., premium access)
- ✅ **Guardrails** to ensure professionalism in replies
- ✅ **Live interaction** with streaming outputs for transparency


---
## 🚀 Features
---


| Feature            | Description |
|--------------------|-------------|
| 🔁 **Triage Agent** | Classifies user intent and delegates to specialist agents |
| 🧾 **Billing Agent** | Handles refunds, invoices, subscriptions |
| 🛠️ **Technical Agent** | Resolves restarts, errors, and connectivity issues |
| 💬 **General Agent** | Answers general or unclassified questions |
| 🛑 **Guardrail Agent** | Blocks apologetic tone (e.g., no “sorry”) |
| 🧰 **Smart Tools** | Tools like `refund()` or `restart_service()` only activate when conditions are met |
| 🧵 **Streaming Output** | Shows responses, handoffs, and tool actions in real time |


---
## 🛠️ Technologies Used
---


| Component           | Description                                   |
|---------------------|-----------------------------------------------|
| 🐍 Python            | Base language for async and logic             |
| 🧠 OpenAI Agents SDK | Multi-agent framework for building AI agents  |
| 🔮 Gemini API        | Model: `gemini-2.5-flash` for completions     |
| 🧱 Pydantic          | Input/output schema validation                |
| 🔐 dotenv            | Environment variable management               |
| 🔁 asyncio           | Asynchronous event loop support               |
| ⚡ uv                | Fast Python package manager & virtualenv tool |


---
## 🧪 Setup Instructions with `uv`
---


> 🧰 **Note:** This project uses [`uv`](https://github.com/astral-sh/uv) — a modern, blazing-fast Python environment manager.

### 🧷 Step 1: Initialize your environment

```bash
uv init
````

### 📦 Step 2: Add required dependencies

```bash
uv add openai-agents
```

### 🔐 Step 3: Activate the environment

```bash
.venv\Scripts\activate  # Windows
# OR
source .venv/bin/activate  # macOS/Linux
```

### 🔑 Step 4: Add your Gemini API key

Create a `.env` file in the root of the project and add:

```env
GEMINI_API_KEY=your-gemini-api-key
```

### 🏃 Step 5: Run the console app

```bash
uv run main.py
```


---
## 💡 Example Interaction
---


```text
🔧 Support System Initialized — type 'exit' to quit.
👤 Enter your name: Ali
⭐ Premium user? (y/N): y

💬 How can I help you? I need a refund.

[ 🧠 Triage in progress… ]
→ Handoff: Billing Agent
→ Tool Call: refund
✅ Refund for Ali initiated; expect 3–5 business days.
```

---
## 📌 Key Notes
---


* 🛑 **Apology guardrail** ensures professional tone by blocking words like “sorry”.
* 🧰 **Contextual tools**: Tools only activate if user conditions are met (e.g., refund is for premium users).
* 🧵 **Streamed feedback**: Real-time console output of all steps—tool calls, handoffs, and agent messages.
