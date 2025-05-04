# 🚗 Smart Mobility Agent – Seamless Routing + Hassle-Free Parking

This project is a unified AI-powered assistant that takes you from **Point A to Point B** in the smartest way possible — and helps you **effortlessly pay for parking** once you arrive.

---

## 🎯 What We're Building

A full-stack agent system that:

✅ Suggests **the best route** from your origin to destination  
✅ Provides **public transport alternatives** to help you save  
✅ Supports **LLM-powered chat** for natural, human-like interaction  
✅ Automatically **pays for your parking** once you reach — no apps, no SMS, no meters

> All through a **single prompt** like:
> _“How do I get from Marina Walk to DIFC, and park for 2 hours?”_

---

## 🧠 Powered By

- **Large Language Models** (LLMs): To extract route & parking info from user messages  
- **Google Maps API**: For real-time directions, durations, and transit suggestions  
- **uAgents Framework**: Modular protocol-based agent design  
- **Parking Integration Layer**: Communicates with major UAE parking providers

---

## 🔁 Seamless Travel Experience

### 🛣️ Step 1: Smart Routing

- You ask:  
  _"What's the best way from Business Bay to Mall of the Emirates?"_

- The agent replies:

Mode: driving
Duration: 16 mins
Distance: 11.2 km
Suggestion: Transit takes 21 mins and is cheaper. Reply "Transit details" to see full route.


---

🗺️ Why This Matters

🧠 No more copying SMS formats  
🅿️ No more searching for parking meters  
🚇 Encourages cost-effective public transport  
📱 Works inside chatbots, apps, or even voice assistants  
🌍 Expandable globally with minimal tweaks

---

📦 Project Modules

| Module             | Purpose |
|--------------------|---------|
| `maps_agent`       | Handles all routing (driving + transit) |
| `parking_agent`    | Processes parking requests and bookings |
| `chat_proto`       | Interprets user input and interacts with LLM agent |
| `agent.py`         | Runs the system and registers protocols |
| `.env`             | Securely stores API tokens |
| `README.md`        | You're here. High-level overview of the full solution |

---

🔧 Configuration & Setup

🧩 Requirements

- Python 3.10+
- Google Maps API Key
- Wassenger (or backend integration) Token

---

🔐 How to Get Your Wassenger API Token

To enable the agent to send parking booking requests, you'll need an API token from [Wassenger](https://www.wassenger.com/), a platform that facilitates programmatic messaging.

🪪 Step-by-Step

1. Go to [https://app.wassenger.com](https://app.wassenger.com) and sign in
2. Add your device (if not already)
3. Navigate to **Settings → API Tokens**
4. Click **"Create Token"**, name it (e.g., `parking-agent`), and copy it
5. In your project, create a `.env` file:

🧪 Sample Prompts to Try
"How to reach City Walk from JLT?"
"Drive to DIFC and park for 1 hour, plate XYZ456"
"Public transport from Business Bay to Airport"
"Book parking in zone A100 for 2 hours"

🔭 Roadmap
📍 GPS-based auto-detection of parking zone
💳 Payment gateway integration (Apple Pay, Google Pay)
🧾 Permit/validation status checks

🤝 Partners
✅ DIFC Parking
✅ Parkin
🚧 RTA, Malls, and more coming soon

