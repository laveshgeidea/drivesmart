# 🅿️ LLM-Powered Smart Parking Assistant

This agent helps you pay for parking using natural language prompts — powered by an intelligent agent framework and LLM-backed schema parsing. It supports major UAE parking providers such as **DIFC Parking**, **Parkin**, and more to come.

---

## 💬 What It Does

This conversational agent:
- Detects the area you’re in
- Understands simple prompts like:  
  _"Park my car in zone A123 for 2 hours"_
- Automatically processes the request through the appropriate parking provider

✅ **No app switching**  
✅ **No SMS formats**  
✅ **Just type a sentence, and you’re parked.**

---

## 🧠 How It Works

1. **User sends a message** in chat with zone and duration.
2. The message is forwarded to an **LLM agent** that extracts:
   - `zone`
   - `car plate`
   - `duration`
3. The structured data is sent to the **Parking Agent**, which initiates the parking request through the backend service.
4. You receive a **confirmation message**.

---

## 📥 Installation & Run

```bash
pip install -r requirements.txt
python agent.py

---

## 🔐 How to Get Your Wassenger API Token

To enable the agent to send parking booking requests, you'll need an API token from [Wassenger](https://www.wassenger.com/), a platform that facilitates programmatic messaging.

### 🪪 Step-by-Step Guide

1. **Sign Up or Log In**
   - Visit [https://app.wassenger.com](https://app.wassenger.com)
   - Create a free account or log into your existing one

2. **Add a Device (if required)**
   - Follow instructions to link your WhatsApp number via their dashboard
   - You may need to scan a QR code from your WhatsApp app

3. **Generate an API Token**
   - In the left sidebar, go to **Settings → API Tokens**
   - Click **"Create Token"**
   - Give it a name like `parking-agent`
   - Click **"Create"** and **copy** the token

4. **Store It Securely**
   - Create a `.env` file at the root of your project (if it doesn't exist)
   - Paste your token like this:

     ```env
     WASSENGER_API_TOKEN=your_copied_token_here
     ```

⚠️ **Never commit your `.env` file to Git**  
Add it to `.gitignore` to protect sensitive credentials.

---

✅ That’s it! Your agent will now be able to send messages through the Wassenger platform using the provided token.
