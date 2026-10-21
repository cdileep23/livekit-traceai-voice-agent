import os

from fi_instrumentation import register
from fi_instrumentation.fi_types import ProjectType
from traceai_livekit import enable_http_attribute_mapping


def configure_tracing() -> bool:
    if not (os.environ.get("FI_API_KEY") and os.environ.get("FI_SECRET_KEY")):
        return False
    register(
        project_type=ProjectType.OBSERVE,
        project_name=os.environ.get("FI_PROJECT_NAME", "harbor-hotels-voice-agent"),
        set_global_tracer_provider=True,
    )
    enable_http_attribute_mapping()
    return True
