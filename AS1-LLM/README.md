# ASI1 Agent Service

This is an intelligent agent implementation built using the `uagents` framework that integrates with the ASI1 LLM API. It provides context-aware chat and structured responses, including health checks and rate-limiting.

---

## 📁 Project Structure

- `agent.py`: Main agent entrypoint that registers three protocols:
  - Context-based response
  - Structured schema response
  - Health check
- `asi1.py`: Handles interaction with the ASI1 LLM API.
- `chat_proto.py`: Handles chat messages using the uAgents chat protocol.

---

## 🧩 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
