# agent.py
import asyncio
from enum import Enum
from uuid import uuid4

from uagents import Agent, Context, Model
from uagents.experimental.quota import QuotaProtocol, RateLimit
from uagents_core.models import ErrorMessage

from chat_proto import chat_proto, struct_output_client_proto
from parking_agent import ParkingRequest, ParkingResponse, process_parking_request

agent = Agent()

parking_protocol = QuotaProtocol(
    storage_reference=agent.storage,
    name="ParkingProtocol",
    version="0.1.0")


@parking_protocol.on_message(ParkingRequest, replies={ParkingResponse, ErrorMessage})
async def handle_route_request(ctx: Context, sender: str, msg: ParkingRequest):
    ctx.logger.info(str(msg))
    ctx.logger.info(f"[1] Received parking request: {msg}")
    try:
        summary = await process_parking_request(msg.zone, msg.number_plate, msg.hours, ctx)
        if "Failed" in summary:
            await ctx.send(sender, ErrorMessage(error=f"[2] {summary}"))
        else:
            await ctx.send(sender, ParkingResponse(results=summary))
    except Exception as err:
        error_message = f"[3] Unhandled error in processing: {str(err)}"
        ctx.logger.error(error_message)
        await ctx.send(sender, ErrorMessage(error=error_message))


class HealthCheck(Model):
    pass


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class AgentHealth(Model):
    agent_name: str
    status: HealthStatus


def agent_is_healthy() -> bool:
    return True


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
        await ctx.send(sender, AgentHealth(agent_name="parking_agent", status=status))


agent.include(parking_protocol, publish_manifest=True)
agent.include(health_protocol, publish_manifest=True)
agent.include(chat_proto, publish_manifest=True)
agent.include(struct_output_client_proto, publish_manifest=True)

if __name__ == "__main__":
    print("agent running")
    agent.run()