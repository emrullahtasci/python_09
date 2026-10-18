"""Exercise 0: Space Station Data - basic Pydantic models with Field."""

from datetime import datetime

from pydantic import BaseModel, Field, ValidationError


class SpaceStation(BaseModel):
    """Vital statistics reported by a space station.

    Every constraint is declared with Field(...). Pydantic checks them all
    when an instance is created and raises ValidationError on bad data.
    """

    # min_length / max_length limit the number of characters of a string
    station_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=1, max_length=50)
    # ge = greater or equal, le = less or equal
    crew_size: int = Field(ge=1, le=20)
    power_level: float = Field(ge=0.0, le=100.0)
    oxygen_level: float = Field(ge=0.0, le=100.0)
    # A string like "2024-01-15T10:30:00" is converted to datetime
    last_maintenance: datetime
    # Plain default value: the field becomes optional when creating
    is_operational: bool = True
    # "str | None" means the field may be missing (None)
    notes: str | None = Field(default=None, max_length=200)


def display_station(station: SpaceStation) -> None:
    """Print the station information in a readable way."""
    status = "Operational" if station.is_operational else "Offline"
    print(f"ID: {station.station_id}")
    print(f"Name: {station.name}")
    print(f"Crew: {station.crew_size} people")
    print(f"Power: {station.power_level}%")
    print(f"Oxygen: {station.oxygen_level}%")
    print(f"Status: {status}")


def main() -> None:
    """Create a valid station, then show how an invalid one is rejected."""
    separator = "=" * 40
    print("Space Station Data Validation")
    print(separator)

    # model_validate() builds the model from raw data such as a dict
    # loaded from JSON. The timestamp is a string here on purpose:
    # Pydantic converts it to a datetime object automatically.
    raw_station = {
        "station_id": "ISS001",
        "name": "International Space Station",
        "crew_size": 6,
        "power_level": 85.5,
        "oxygen_level": 92.3,
        "last_maintenance": "2024-01-15T10:30:00",
    }
    try:
        station = SpaceStation.model_validate(raw_station)
        print("Valid station created:")
        display_station(station)
    except ValidationError as error:
        print(f"Unexpected error: {error}")
    print(separator)

    # crew_size is above the allowed maximum (le=20)
    try:
        SpaceStation(
            station_id="ISS002",
            name="Overcrowded Station",
            crew_size=25,
            power_level=50.0,
            oxygen_level=50.0,
            last_maintenance=datetime(2024, 1, 15),
        )
        print("ERROR: invalid station was accepted")
    except ValidationError as error:
        print("Expected validation error:")
        # errors() returns one dict per failed field, "msg" is readable
        for detail in error.errors():
            print(detail["msg"])


if __name__ == "__main__":
    main()
