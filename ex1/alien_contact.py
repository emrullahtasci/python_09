"""Exercise 1: Alien Contact Logs - custom rules with @model_validator."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, model_validator


class ContactType(str, Enum):
    """Allowed kinds of contact. Any other value is rejected."""

    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    """A single alien contact report."""

    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: str | None = Field(default=None, max_length=500)
    is_verified: bool = False

    @model_validator(mode="after")
    def check_business_rules(self) -> "AlienContact":
        """Rules that involve several fields at once."""
        if not self.contact_id.startswith("AC"):
            raise ValueError("Contact ID must start with 'AC'")
        if (self.contact_type == ContactType.PHYSICAL
                and not self.is_verified):
            raise ValueError("Physical contact reports must be verified")
        if (self.contact_type == ContactType.TELEPATHIC
                and self.witness_count < 3):
            raise ValueError(
                "Telepathic contact requires at least 3 witnesses"
            )
        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError("Strong signals (> 7.0) must include a message")
        return self


def error_messages(error: ValidationError) -> list[str]:
    """Return clean messages from a ValidationError.

    For a ValueError raised in a validator, Pydantic prefixes the message
    with "Value error, ". The original exception is kept in ctx["error"],
    so we print that one instead.
    """
    messages = []
    for detail in error.errors():
        ctx = detail.get("ctx", {})
        if detail["type"] == "value_error" and "error" in ctx:
            messages.append(str(ctx["error"]))
        else:
            messages.append(detail["msg"])
    return messages


def display_contact(contact: AlienContact) -> None:
    """Print a contact report."""
    print(f"ID: {contact.contact_id}")
    print(f"Type: {contact.contact_type.value}")
    print(f"Location: {contact.location}")
    print(f"Signal: {contact.signal_strength}/10")
    print(f"Duration: {contact.duration_minutes} minutes")
    print(f"Witnesses: {contact.witness_count}")
    if contact.message_received:
        print(f"Message: '{contact.message_received}'")


def main() -> None:
    """Show one valid report and one report breaking a business rule."""
    separator = "=" * 38
    print("Alien Contact Log Validation")
    print(separator)

    try:
        contact = AlienContact(
            contact_id="AC_2024_001",
            timestamp=datetime(2024, 7, 2, 23, 47),
            location="Area 51, Nevada",
            contact_type=ContactType.RADIO,
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=5,
            message_received="Greetings from Zeta Reticuli",
        )
        print("Valid contact report:")
        display_contact(contact)
    except ValidationError as error:
        print(f"Unexpected error: {error}")
    print(separator)

    try:
        AlienContact(
            contact_id="AC_2024_002",
            timestamp=datetime(2024, 7, 3, 3, 15),
            location="Roswell, New Mexico",
            contact_type=ContactType.TELEPATHIC,
            signal_strength=4.0,
            duration_minutes=10,
            witness_count=2,
        )
        print("ERROR: invalid report was accepted")
    except ValidationError as error:
        print("Expected validation error:")
        for message in error_messages(error):
            print(message)


if __name__ == "__main__":
    main()
