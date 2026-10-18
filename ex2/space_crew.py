"""Exercise 2: Space Crew Management - nested Pydantic models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    """Crew ranks, from lowest to highest."""

    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    """One member of a mission crew."""

    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    """A mission and its crew.

    crew is a list of CrewMember models: Pydantic validates each member
    first. If one member is invalid, the whole mission is rejected and
    the error location shows which one (e.g. crew.1.age).
    """

    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    # On a list, min_length / max_length limit the number of items
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def check_safety_rules(self) -> "SpaceMission":
        """Safety requirements that look at the whole crew."""
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        leaders = [
            member for member in self.crew
            if member.rank in (Rank.COMMANDER, Rank.CAPTAIN)
        ]
        if not leaders:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        if self.duration_days > 365:
            experienced = [
                member for member in self.crew
                if member.years_experience >= 5
            ]
            # At least half of the crew: experienced / crew >= 0.5
            if len(experienced) * 2 < len(self.crew):
                raise ValueError(
                    "Long missions (> 365 days) need at least 50% "
                    "experienced crew (5+ years)"
                )

        inactive = [m.name for m in self.crew if not m.is_active]
        if inactive:
            raise ValueError(
                f"All crew members must be active: {', '.join(inactive)}"
            )
        return self


def error_messages(error: ValidationError) -> list[str]:
    """Return clean messages, without Pydantic's "Value error, " prefix."""
    messages = []
    for detail in error.errors():
        ctx = detail.get("ctx", {})
        if detail["type"] == "value_error" and "error" in ctx:
            messages.append(str(ctx["error"]))
        else:
            messages.append(detail["msg"])
    return messages


def display_mission(mission: SpaceMission) -> None:
    """Print mission details and its crew list."""
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for member in mission.crew:
        print(f"- {member.name} ({member.rank.value})"
              f" - {member.specialization}")


def main() -> None:
    """Show a valid mission and one that fails the safety rules."""
    separator = "=" * 41
    print("Space Mission Crew Validation")
    print(separator)

    crew = [
        CrewMember(member_id="CM001", name="Sarah Connor",
                   rank=Rank.COMMANDER, age=45,
                   specialization="Mission Command", years_experience=20),
        CrewMember(member_id="CM002", name="John Smith",
                   rank=Rank.LIEUTENANT, age=35,
                   specialization="Navigation", years_experience=10),
        CrewMember(member_id="CM003", name="Alice Johnson",
                   rank=Rank.OFFICER, age=29,
                   specialization="Engineering", years_experience=4),
    ]
    try:
        mission = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date=datetime(2024, 9, 1, 9, 0),
            duration_days=900,
            crew=crew,
            budget_millions=2500.0,
        )
        print("Valid mission created:")
        display_mission(mission)
    except ValidationError as error:
        print(f"Unexpected error: {error}")
    print(separator)

    # Same kind of mission, but nobody is a Commander or a Captain
    try:
        SpaceMission(
            mission_id="M2024_MOON",
            mission_name="Lunar Survey",
            destination="Moon",
            launch_date=datetime(2024, 12, 1),
            duration_days=30,
            crew=[
                CrewMember(member_id="CM004", name="Tom Hardy",
                           rank=Rank.OFFICER, age=30,
                           specialization="Geology", years_experience=6),
                CrewMember(member_id="CM005", name="Lisa Ray",
                           rank=Rank.CADET, age=22,
                           specialization="Communications",
                           years_experience=1),
            ],
            budget_millions=300.0,
        )
        print("ERROR: invalid mission was accepted")
    except ValidationError as error:
        print("Expected validation error:")
        for message in error_messages(error):
            print(message)


if __name__ == "__main__":
    main()
