import os
import requests
from uagents import Model, Field

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLEAPI")

class RouteRequest(Model):
    start_location: str
    end_location: str
    mode: str = Field(default="driving")

class RouteResponse(Model):
    results: str

async def get_route_info(start_location: str, end_location: str, mode: str = "driving") -> str:
    """
    Fetch route info from Google Maps and return as plain-text summary.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": start_location,
        "destination": end_location,
        "mode": mode,
        "key": GOOGLE_MAPS_API_KEY
    }
    if mode == "driving":
        params["departure_time"] = "now"

    resp = requests.get(url, params=params).json()
    if not resp.get("routes"):
        return "No route found."

    route = resp["routes"][0]
    leg = route["legs"][0]

    # Duration
    if mode == "driving":
        duration = leg.get("duration_in_traffic", leg["duration"]).get("text")
    else:
        duration = leg["duration"].get("text")

    distance = leg["distance"].get("text")

    # Fare / cost for transit
    fare_text = route.get("fare", {}).get("text")

    # Count transit steps to estimate transfers
    transfers = None
    if mode == "transit":
        transit_steps = [step for step in leg.get("steps", []) if step.get("travel_mode") == "TRANSIT"]
        if len(transit_steps) > 1:
            transfers = len(transit_steps) - 1

    # Start and end addresses
    start = leg.get("start_address", start_location)
    end = leg.get("end_address", end_location)

    # Build result lines
    lines = [
        f"Mode: {mode}",
        f"Duration: {duration}",
        f"Distance: {distance}"
    ]
    if fare_text:
        lines.append(f"Fare: {fare_text}")
    if transfers is not None:
        lines.append(f"Transfers: {transfers}")
    lines.extend([
        f"From: {start}",
        f"To:   {end}"
    ])

    return "\n".join(lines)
