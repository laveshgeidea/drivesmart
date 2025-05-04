# 🗺️ Smart Maps Agent with Conversational Interface

This is an intelligent conversational agent built on [uAgents](https://github.com/bitclout/uAgents) that allows users to ask for routes using natural language and get back structured responses for **driving** or **transit** using the Google Maps API.

The agent leverages:
- 🤖 **LLMs** for understanding user prompts and converting them into structured route requests.
- 🗺️ **Google Maps API** for fetching real-world route data.
- 💬 **uAgents chat protocol** for interactive, asynchronous messaging.

---

## 🚦 Use Case Example

> “How do I get from Dubai Marina to Mall of the Emirates?”

The agent will:
1. Use an LLM to extract `start_location`, `end_location`, and preferred `mode` (e.g., driving).
2. Query Google Maps for a **driving route summary**.
3. Automatically fetch and suggest a **public transit alternative**.
4. Provide a friendly recommendation:
   - “Want to try public transit? It takes 25 mins but might save you money. Reply with 'Transit details' to explore that option.”

---

## 🧱 Architecture Overview

```plaintext
┌──────────────────────┐
│  User Message (Text) │
└─────────┬────────────┘
          │
          ▼
┌────────────────────────────────────────────┐
│ Chat Protocol (chat_proto.py)              │
│  - Forwards text to LLM agent              │
│  - Recognizes follow-up like 'transit...'  │
│  - Stores sessions and past queries        │
└─────────┬──────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────┐
│ LLM Agent (via AI_AGENT_ADDRESS)   │
│  - Parses prompt into schema       │
│  - Sends RouteRequest              │
└─────────┬──────────────────────────┘
          ▼
┌───────────────────────────────────────┐
│ Maps Agent (maps_agent.py)            │
│  - Fetches route from Google Maps API │
│  - Computes driving + transit options │
│  - Returns combined summary           │
└───────────────────────────────────────┘
          │
          ▼
  👤 Final response prettified and sent

