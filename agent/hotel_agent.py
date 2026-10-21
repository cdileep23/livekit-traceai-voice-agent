from livekit.agents import Agent, function_tool

from . import tools

INSTRUCTIONS = (
    "You are the phone booking assistant for Harbor Hotels. You are speaking on a voice call, "
    "so keep every reply to one or two short sentences, with no lists or symbols. "
    "Help callers find hotels by city and budget, look up bookings and cancel confirmed bookings. "
    "Always use the tools for availability, rates and bookings; never guess. "
    "Booking ids look like HB-5001; read them back to confirm before acting. "
    "Ask for the booking id when the caller has not given one. "
    "Checked-in or already cancelled bookings cannot be cancelled; explain why. "
    "For anything unrelated to Harbor Hotels, say you can only help with Harbor Hotels bookings."
)

GREETING = "Thanks for calling Harbor Hotels. How can I help you today?"


class HotelAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.say(GREETING, allow_interruptions=True)

    @function_tool
    async def find_hotels(self, city: str, max_nightly_rate: int | None = None) -> list[dict]:
        """List Harbor Hotels in a city, optionally under a nightly rate, with rooms left.

        Args:
            city: The city the caller wants to stay in.
            max_nightly_rate: The most the caller will pay per night, if they said.
        """
        return tools.find_hotels(city, max_nightly_rate)

    @function_tool
    async def get_booking(self, booking_id: str) -> dict:
        """Look up a booking by its id, for example HB-5001.

        Args:
            booking_id: The booking id the caller gave.
        """
        return tools.get_booking(booking_id)

    @function_tool
    async def cancel_booking(self, booking_id: str) -> dict:
        """Cancel a confirmed booking. Checked-in or already cancelled bookings cannot be cancelled.

        Args:
            booking_id: The booking id the caller confirmed.
        """
        return tools.cancel_booking(booking_id)
