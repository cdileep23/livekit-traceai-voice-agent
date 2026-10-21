# Harbor Hotels voice agent (LiveKit, traceAI)

A phone booking assistant for Harbor Hotels, a fictional hotel chain. It is the voice twin of
`langchain-traceai-agent`: same hotels, same bookings, same three tools, served as a LiveKit
Agents voice pipeline (Deepgram speech-to-text, Claude, Deepgram text-to-speech, Silero VAD)
and traced with Future AGI's traceAI (`fi_instrumentation` + `traceai_livekit`).

## Tools

| Tool             | Arguments                    | Behaviour                                                |
|------------------|------------------------------|----------------------------------------------------------|
| `find_hotels`    | `city`, `max_nightly_rate`   | Hotels in a city, optionally under a nightly rate.       |
| `get_booking`    | `booking_id`                 | Guest, hotel, dates and status of a booking.             |
| `cancel_booking` | `booking_id`                 | Cancels only a confirmed booking.                        |

Fixture bookings: `HB-5001` confirmed (cancellable), `HB-5002` checked in, `HB-5003` cancelled.
Any other id is not found. Hotels exist in Lisbon, Berlin and Tokyo. Data is in memory and
resets on restart.

## Tracing

`agent/tracing.py` runs inside the LiveKit entrypoint, as traceAI-livekit requires for
LiveKit's worker processes. When `FI_API_KEY` and `FI_SECRET_KEY` are both set it calls
`register(project_type=OBSERVE, set_global_tracer_provider=True)` and then
`enable_http_attribute_mapping()`, which maps LiveKit's own spans (`lk.*`, `gen_ai.*`) to Future
AGI attributes and hands the provider to `livekit.agents.telemetry`. Without both keys it sends
nothing.

## Configuration

| Variable                                         | Purpose                                                    |
|--------------------------------------------------|------------------------------------------------------------|
| `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` | Required. The LiveKit project the worker joins.       |
| `LIVEKIT_AGENT_NAME`                             | Optional, default `harbor-hotels-voice`.                   |
| `DEEPGRAM_API_KEY`                               | Required. Speech-to-text and text-to-speech.               |
| `ANTHROPIC_API_KEY`                              | Required. The Anthropic API key. |
| `AGENT_STT_MODEL`, `AGENT_LLM_MODEL`, `AGENT_TTS_MODEL` | Optional. Defaults `nova-3`, `claude-haiku-5-5`, `aura-2-andromeda-en`. |
| `FI_API_KEY`, `FI_SECRET_KEY`                    | Optional. When both are set, traceAI sends traces.         |
| `FI_PROJECT_NAME`                                | Optional, default `harbor-hotels-voice-agent`.             |
| `HARNESS_CALLER_IDENTITY_PREFIX`                 | Set by the simulation harness; the agent waits for that caller. |

## Running it

```
uv sync
uv run python -m livekit.agents download-files
cp .env.example .env.local   # fill in the keys
uv run python -m agent.agent dev
```

Tests: `uv run pytest`.
