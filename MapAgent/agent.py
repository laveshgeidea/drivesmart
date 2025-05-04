import asyncio
from enum import Enum
from uuid import uuid4

from uagents import Agent, Context, Model
from uagents.experimental.quota import QuotaProtocol, RateLimit
from uagents_core.models import ErrorMessage

from chat_proto import chat_proto, struct_output_client_proto
from maps_agent import get_route_info, RouteRequest, RouteResponse

agent = Agent()

maps_protocol = QuotaProtocol(
    storage_reference=agent.storage,
    name="MapsProtocol",
    version="0.1.0",
    default_rate_limit=RateLimit(window_size_minutes=60, max_requests=30),
)

@maps_protocol.on_message(RouteRequest, replies={RouteResponse, ErrorMessage})
async def handle_route_request(ctx: Context, sender: str, msg: RouteRequest):
    ctx.logger.info(f"Received route request: {msg}")
    try:
        summary = await get_route_info(msg.start_location, msg.end_location, msg.mode)
        await ctx.send(sender, RouteResponse(results=summary))
    except Exception as err:
        ctx.logger.error(err)
        await ctx.send(sender, ErrorMessage(error=str(err)))

# --- Health check wiring ---
class HealthCheck(Model):
    pass

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class AgentHealth(Model):
    agent_name: str
    status: HealthStatus

def agent_is_healthy() -> bool:
    """
    E.g. try a dummy route lookup to make sure Google Maps is reachable.
    """
    try:
        # we do this synchronously to keep it simple
        import requests
        params = {
            "origin": "Dubai Mall",
            "destination": "Dubai Airport",
            "mode": "driving",
            "key": os.environ.get("GOOGLEAPI")
        }
        resp = requests.get("https://maps.googleapis.com/maps/api/directions/json", params=params).json()
        return bool(resp.get("routes"))
    except Exception:
        return False

health_protocol = QuotaProtocol(
    storage_reference=agent.storage,
    name="HealthProtocol",
    version="0.1.0"
)

@health_protocol.on_message(HealthCheck, replies={AgentHealth})
async def handle_health_check(ctx: Context, sender: str, msg: HealthCheck):
    status = HealthStatus.UNHEALTHY
    try:
        if agent_is_healthy():
            status = HealthStatus.HEALTHY
    except Exception as err:
        ctx.logger.error(err)
    finally:
        await ctx.send(sender, AgentHealth(agent_name="maps_agent", status=status))

# --- Include all protocols and run ---
agent.include(maps_protocol, publish_manifest=True)
agent.include(health_protocol, publish_manifest=True)
agent.include(chat_proto, publish_manifest=True)
agent.include(struct_output_client_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()