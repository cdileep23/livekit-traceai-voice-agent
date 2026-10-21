import asyncio
import logging
import os

from dotenv import load_dotenv
from livekit.agents import AgentServer, AgentSession, JobContext, cli, room_io
from livekit.plugins import anthropic, deepgram, silero

from agent.hotel_agent import HotelAgent
from agent.tracing import configure_tracing

load_dotenv(".env.local")
logger = logging.getLogger("harbor-hotels-voice-agent")

server = AgentServer()


def build_stt(api_key: str, model: str):
    if model.startswith("flux-"):
        return deepgram.STTv2(api_key=api_key, model=model)
    return deepgram.STT(api_key=api_key, model=model)


async def wait_for_caller(ctx: JobContext):
    identity_prefix = os.environ.get("HARNESS_CALLER_IDENTITY_PREFIX", "").strip()
    if not identity_prefix:
        return await ctx.wait_for_participant()
    await ctx.connect()
    deadline = asyncio.get_running_loop().time() + 60
    while asyncio.get_running_loop().time() < deadline:
        for participant in ctx.room.remote_participants.values():
            if str(participant.identity).startswith(identity_prefix):
                return participant
        await asyncio.sleep(0.1)
    raise RuntimeError(f"caller participant with prefix {identity_prefix!r} did not join")


@server.rtc_session(agent_name=os.environ.get("LIVEKIT_AGENT_NAME", "harbor-hotels-voice"))
async def entrypoint(ctx: JobContext) -> None:
    traced = configure_tracing()
    logger.info("tracing configured", extra={"traced": traced})
    participant = await wait_for_caller(ctx)
    deepgram_key = os.environ["DEEPGRAM_API_KEY"]
    session = AgentSession(
        stt=build_stt(deepgram_key, os.environ.get("AGENT_STT_MODEL", "nova-3")),
        llm=anthropic.LLM(
            model=os.environ.get("AGENT_LLM_MODEL", "claude-haiku-5-5"),
            temperature=float(os.environ.get("AGENT_LLM_TEMPERATURE", "0.2")),
            api_key=os.environ["ANTHROPIC_API_KEY"],
        ),
        tts=deepgram.TTS(
            api_key=deepgram_key,
            model=os.environ.get("AGENT_TTS_MODEL", "aura-2-andromeda-en"),
        ),
        vad=silero.VAD.load(),
        max_tool_steps=int(os.environ.get("AGENT_MAX_TOOL_STEPS", "6")),
    )
    await session.start(
        agent=HotelAgent(),
        room=ctx.room,
        room_options=room_io.RoomOptions(participant_identity=participant.identity),
    )


if __name__ == "__main__":
    cli.run_app(server)
