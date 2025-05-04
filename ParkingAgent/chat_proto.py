# chat_proto.py
from datetime import datetime
from uuid import uuid4
from typing import Any

from uagents import Context, Model, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

from parking_agent import ParkingRequest, process_parking_request

AI_AGENT_ADDRESS = 'agent1qw2tzlm7u4x4glvsqx5kls2r2tedantmmaqe7qxdhttw00m920d9j395586'
PRETTY_AGENT_ADDRESS = 'agent1qw2tzlm7u4x4glvsqx5kls2r2tedantmmaqe7qxdhttw00m920d9j395586'

def create_text_chat(text: str, end_session: bool = True) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(timestamp=datetime.utcnow(), msg_id=uuid4(), content=content)

chat_proto = Protocol(spec=chat_protocol_spec)
struct_output_client_proto = Protocol(
    name="StructuredOutputClientProtocol",
    version="0.1.0"
)

class StructuredOutputPrompt(Model):
    prompt: str
    output_schema: dict[str, Any]

class StructuredOutputResponse(Model):
    output: dict[str, Any]

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    if sender == PRETTY_AGENT_ADDRESS:
        session_sender = ctx.storage.get(str(ctx.session))
        for item in msg.content:
            if isinstance(item, TextContent):
                await ctx.send(session_sender, create_text_chat(item.text))
        return

    ctx.storage.set(str(ctx.session), sender)
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id),
    )

    # 👇 Updated prompt to ask for just field values
    extraction_instruction = (
        "Extract explicitly from the user's message:\n"
        "- Zone (string)\n- Number plate (string)\n- Hours (string or integer)\n\n"
        "Respond ONLY with a JSON object with these fields and their values, like:\n"
        '{\n  "zone": "XYZ123",\n  "number_plate": "ABC123",\n  "hours": "2"\n}\n\n'
        f"User message: \"{msg.content[0].text}\""
    )

    for item in msg.content:
        if isinstance(item, TextContent):
            await ctx.send(
                AI_AGENT_ADDRESS,
                StructuredOutputPrompt(
                    prompt=extraction_instruction,
                    output_schema={
                        "type": "object",
                        "properties": {
                            "zone": {"type": "string"},
                            "number_plate": {"type": "string"},
                            "hours": {"type": "string"}
                        },
                        "required": ["zone", "number_plate"]
                    }
                ),
            )

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"[5] Ack from {sender} for {msg.acknowledged_msg_id}")

@struct_output_client_proto.on_message(StructuredOutputResponse)
async def handle_structured_output_response(ctx: Context, sender: str, msg: StructuredOutputResponse):
    ctx.logger.info(f"[11] AI output received: {msg.output}")

    session_sender = ctx.storage.get(str(ctx.session))
    if session_sender is None:
        ctx.logger.error("[6] No session sender found.")
        return

    if "<UNKNOWN>" in str(msg.output):
        await ctx.send(session_sender, create_text_chat("[7] Couldn't parse message."))
        return

    # ✅ Ensure required keys exist before parsing
    if not all(k in msg.output for k in ["zone", "number_plate"]):
        await ctx.send(session_sender, create_text_chat("[12] Missing required fields in AI output."))
        return

    try:
        req = ParkingRequest.parse_obj(msg.output)
        summary = await process_parking_request(req.zone, req.number_plate, req.hours, ctx)

        if "[3]" in summary or "[4]" in summary:
            await ctx.send(session_sender, create_text_chat(f"[8] Error: {summary}"))
        else:
            await ctx.send(PRETTY_AGENT_ADDRESS, create_text_chat(summary, end_session=True))

    except Exception as err:
        ctx.logger.error(f"[9] Unhandled error: {str(err)}")
        await ctx.send(session_sender, create_text_chat(f"[10] Error processing: {str(err)}"))
