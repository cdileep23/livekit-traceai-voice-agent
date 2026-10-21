import importlib

import pytest

from agent import store, tools


@pytest.fixture(autouse=True)
def fresh_bookings(monkeypatch):
    monkeypatch.setattr(
        store, "BOOKINGS", {key: dict(value) for key, value in store.BOOKINGS.items()}
    )
    monkeypatch.setattr(tools, "BOOKINGS", store.BOOKINGS)


def test_find_hotels_filters_by_city_and_rate():
    names = [hotel["name"] for hotel in tools.find_hotels(" lisbon ", 120)]

    assert names == ["Harbor Lisbon Old Town"]


def test_get_booking_reports_unknown_ids():
    assert tools.get_booking("hb-9999") == {"found": False, "booking_id": "hb-9999"}
    assert tools.get_booking("hb-5001")["guest"] == "Ana Silva"


@pytest.mark.parametrize(
    ("booking_id", "expected"),
    [
        ("HB-5001", {"cancelled": True, "booking_id": "HB-5001"}),
        ("HB-5002", {"cancelled": False, "error": "booking_is_checked_in"}),
        ("HB-5003", {"cancelled": False, "error": "booking_is_cancelled"}),
        ("HB-0000", {"cancelled": False, "error": "booking_not_found"}),
    ],
)
def test_cancel_booking_only_cancels_confirmed(booking_id, expected):
    assert tools.cancel_booking(booking_id) == expected


def test_tracing_stays_off_without_both_keys(monkeypatch):
    tracing = importlib.import_module("agent.tracing")
    calls = []
    monkeypatch.setattr(tracing, "register", lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr(tracing, "enable_http_attribute_mapping", lambda: calls.append("map"))
    monkeypatch.setenv("FI_API_KEY", "key")
    monkeypatch.delenv("FI_SECRET_KEY", raising=False)

    assert tracing.configure_tracing() is False
    assert calls == []


def test_tracing_registers_and_maps_with_both_keys(monkeypatch):
    tracing = importlib.import_module("agent.tracing")
    calls = []
    monkeypatch.setattr(tracing, "register", lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr(tracing, "enable_http_attribute_mapping", lambda: calls.append("map"))
    monkeypatch.setenv("FI_API_KEY", "key")
    monkeypatch.setenv("FI_SECRET_KEY", "secret")
    monkeypatch.delenv("FI_PROJECT_NAME", raising=False)

    assert tracing.configure_tracing() is True
    assert calls[0]["project_name"] == "harbor-hotels-voice-agent"
    assert calls[0]["set_global_tracer_provider"] is True
    assert calls[1] == "map"
