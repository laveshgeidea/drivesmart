from datetime import datetime
from uuid import uuid4
from typing import Any

from uagents import Context, Model, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

from maps_agent import get_route_info, RouteRequest

# Addresses for downstream agents
AI_AGENT_ADDRESS = 'agent1qvk7q2av3e2y5gf5s90nfzkc8a48q3wdqeevwrtgqfdl0k78rspd6f2l4dx'
PRETTY_AGENT_ADDRESS = 'agent1qw2tzlm7u4x4glvsqx5kls2r2tedantmmaqe7qxdhttw00m920d9j395586'

if not AI_AGENT_ADDRESS:
    raise ValueError("AI_AGENT_ADDRESS not set")


def create_text_chat(text: str, end_session: bool = True) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=content,
    )

chat_proto = Protocol(spec=chat_protocol_spec)
struct_output_client_proto = Protocol(name="StructuredOutputClientProtocol", version="0.1.0")

class StructuredOutputPrompt(Model):
    prompt: str
    output_schema: dict[str, Any]

class StructuredOutputResponse(Model):
    output: dict[str, Any]

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    # Forward prettified responses directly to the user
    if sender == PRETTY_AGENT_ADDRESS:
        session_sender = ctx.storage.get(str(ctx.session))
        for item in msg.content:
            if isinstance(item, TextContent):
                await ctx.send(session_sender, create_text_chat(item.text))
        return

    # Intercept a 'transit details' follow-up from the user
    for item in msg.content:
        if isinstance(item, TextContent):
            text = item.text.strip().lower()
            if text == "transit details":
                last_query = ctx.storage.get(f"{ctx.session}_last_query")
                session_sender = ctx.storage.get(str(ctx.session))
                if last_query:
                    start_loc, end_loc = last_query
                    # Fetch transit details (will include detailed steps if supported)
                    detailed = await get_route_info(start_loc, end_loc, "transit")
                    await ctx.send(PRETTY_AGENT_ADDRESS, create_text_chat(detailed, end_session=True))
                else:
                    await ctx.send(session_sender, create_text_chat(
                        "Sorry, I don't have a previous route to show details for."
                    ))
                return

    # Handle a new user message: acknowledge, store, and forward for parsing
    ctx.logger.info(f"Got a message from {sender}: {msg.content[0].text}")
    ctx.storage.set(str(ctx.session), sender)
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id),
    )

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            continue
        elif isinstance(item, TextContent):
            await ctx.send(
                AI_AGENT_ADDRESS,
                StructuredOutputPrompt(
                    prompt=item.text,
                    output_schema=RouteRequest.schema()
                ),
            )

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Ack from {sender} for {msg.acknowledged_msg_id}")

@struct_output_client_proto.on_message(StructuredOutputResponse)
async def handle_structured_output_response(ctx: Context, sender: str, msg: StructuredOutputResponse):
    session_sender = ctx.storage.get(str(ctx.session))
    if session_sender is None:
        ctx.logger.error("No session sender in storage; dropping response")
        return

    if "<UNKNOWN>" in str(msg.output):
        await ctx.send(session_sender, create_text_chat(
            "Sorry, I couldn't parse that. Please try asking in a different way."
        ))
        return

    # Parse into our RouteRequest and stash for follow-ups
    req = RouteRequest.parse_obj(msg.output)
    ctx.storage.set(f"{ctx.session}_last_query", (req.start_location, req.end_location))

    try:
        # Fetch driving and transit summaries
        summary = await get_route_info(req.start_location, req.end_location, req.mode)
        transit_summary = await get_route_info(req.start_location, req.end_location, "transit")
    except Exception as err:
        ctx.logger.error(err)
        await ctx.send(session_sender, create_text_chat(
            "Sorry, something went wrong fetching your route."
        ))
        return

    # Extract transit duration for suggestion
    transit_lines = transit_summary.splitlines()
    transit_duration = None
    for line in transit_lines:
        if line.startswith("Duration:"):
            transit_duration = line.split("Duration:")[1].strip()
            break

    suggestion = ""
    if transit_duration:
        suggestion = (
            f"Psst: Want to try public transit? It takes {transit_duration} but is usually cheaper. "
            "Reply 'Transit details' to dive deeper into it."
        )

    # Combine raw summary and suggestion
    combined_text = summary
    if suggestion:
        combined_text += f"\n\n{suggestion}"

    # Send to prettify agent
    await ctx.send(
        PRETTY_AGENT_ADDRESS,
        create_text_chat(combined_text, end_session=False)
    )

# Export protocols
chat_proto = chat_proto
struct_output_client_proto = struct_output_client_proto
