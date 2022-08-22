from typing import NamedTuple

from starlette.websockets import WebSocket

from src.game import Game


class GameState(NamedTuple):
    is_active: bool
    state: str
    message: str
    player_ws1: WebSocket | None
    player_ws2: WebSocket | None


class PlayersWebSocket(NamedTuple):
    player_ws1: WebSocket | None
    player_ws2: WebSocket | None


class GameInterface(NamedTuple):
    key: int
    game: Game
