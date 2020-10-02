import dataclasses
import datetime
from typing import List, Dict, Optional

from randovania.layout.preset import Preset
from randovania.network_common.session_state import GameSessionState


@dataclasses.dataclass(frozen=True)
class GameSessionListEntry:
    id: int
    name: str
    has_password: bool
    state: GameSessionState
    num_players: int
    creator: str

    @classmethod
    def from_json(cls, data: dict) -> "GameSessionListEntry":
        data["state"] = GameSessionState(data["state"])
        return GameSessionListEntry(**data)


@dataclasses.dataclass(frozen=True)
class PlayerSessionEntry:
    id: int
    name: str
    row: int
    is_observer: bool
    admin: bool

    @classmethod
    def from_json(cls, data) -> "PlayerSessionEntry":
        return PlayerSessionEntry(
            id=data["id"],
            name=data["name"],
            row=data["row"],
            is_observer=data["is_observer"],
            admin=data["admin"],
        )


@dataclasses.dataclass(frozen=True)
class GameSessionAction:
    message: str
    time: datetime.datetime

    @classmethod
    def from_json(cls, data) -> "GameSessionAction":
        return GameSessionAction(
            message=data["message"],
            time=datetime.datetime.fromisoformat(data["time"]),
        )


@dataclasses.dataclass(frozen=True)
class GameSessionEntry:
    id: int
    name: str
    presets: List[Preset]
    players: Dict[int, PlayerSessionEntry]
    actions: List[GameSessionAction]
    seed_hash: Optional[str]
    word_hash: Optional[str]
    spoiler: Optional[bool]
    state: GameSessionState
    generation_in_progress: Optional[int]

    @property
    def num_admins(self) -> int:
        return sum(1 for player in self.players.values() if player.admin)

    @property
    def num_rows(self) -> int:
        return len(self.presets)

    @classmethod
    def from_json(cls, data) -> "GameSessionEntry":
        player_entries = [
            PlayerSessionEntry.from_json(player_json)
            for player_json in data["players"]
        ]
        return GameSessionEntry(
            id=data["id"],
            name=data["name"],
            presets=[Preset.from_json_dict(preset_json) for preset_json in data["presets"]],
            players={
                player_entry.id: player_entry
                for player_entry in player_entries
            },
            actions=[GameSessionAction.from_json(item) for item in data["actions"]],
            seed_hash=data["seed_hash"],
            word_hash=data["word_hash"],
            spoiler=data["spoiler"],
            state=GameSessionState(data["state"]),
            generation_in_progress=data["generation_in_progress"],
        )


@dataclasses.dataclass(frozen=True)
class User:
    id: int
    name: str

    @classmethod
    def from_json(cls, data) -> "User":
        return cls(
            id=data["id"],
            name=data["name"],
        )

    @property
    def as_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }