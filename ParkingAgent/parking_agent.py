import requests
from uagents import Model, Field, Context
import os

class ParkingRequest(Model):
    zone: str
    number_plate: str
    hours: str = Field(default="1")

class ParkingResponse(Model):
    results: str

async def process_parking_request(zone: str, number_plate: str, hours: str, ctx: Context):
    whatsapp_url = "https://api.wassenger.com/v1/messages"

    message_text = f"Parking booked successfully!\nCar Plate: {number_plate}\nZone: {zone}\nDuration: {hours} hour(s)."
    send_text = f"{number_plate} {zone} {hours}"

    WASSENGER_API_TOKEN = os.getenv("WASSENGER_API_TOKEN")

    payload = {
        "phone": "+971588009090",
        "message": send_text
    }

    headers = {
        "Content-Type": "application/json",
        "Token": WASSENGER_API_TOKEN
    }

    try:
        response = requests.post(whatsapp_url, json=payload, headers=headers)
        response.raise_for_status()

        ctx.logger.info("[1] WhatsApp message sent successfully.")
        ctx.logger.info(f"[2] Response: {response.json()}")

        return message_text

    except requests.exceptions.HTTPError as http_err:
        error_msg = f"[3] HTTP error: {http_err}"
        ctx.logger.error(error_msg)
        return error_msg

    except Exception as err:
        error_msg = f"[4] Unexpected error: {err}"
        ctx.logger.error(error_msg)
        return error_msg