from .store import BOOKINGS, HOTELS


def find_hotels(city: str, max_nightly_rate: int | None = None) -> list[dict]:
    wanted = city.strip().lower()
    return [
        hotel
        for hotel in HOTELS
        if hotel["city"].lower() == wanted
        and (max_nightly_rate is None or hotel["nightly_rate"] <= max_nightly_rate)
    ]


def get_booking(booking_id: str) -> dict:
    key = booking_id.strip().upper()
    booking = BOOKINGS.get(key)
    if booking is None:
        return {"found": False, "booking_id": booking_id}
    return {"found": True, "booking_id": key, **booking}


def cancel_booking(booking_id: str) -> dict:
    key = booking_id.strip().upper()
    booking = BOOKINGS.get(key)
    if booking is None:
        return {"cancelled": False, "error": "booking_not_found"}
    if booking["status"] != "confirmed":
        return {"cancelled": False, "error": f"booking_is_{booking['status']}"}
    booking["status"] = "cancelled"
    return {"cancelled": True, "booking_id": key}
