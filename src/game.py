from typing import List, Tuple, Literal, NamedTuple
from starlette.websockets import WebSocket

from src.auth.models import User


class MoveGame(NamedTuple):
    state: Literal['X', 'O']
    message: str
    is_active: bool
    is_won: bool
    is_draw: bool
    player_won: str | None
    player_loss: str | None


class Player:
    def __init__(
            self, ws: WebSocket, state: Literal['X'] | Literal['O'] = 'X', username: str = None
    ) -> None:
        self.__ws = ws
        self.__state = state
        self.__username = username

    def check_ws(self, ws: WebSocket) -> bool:
        return ws == self.__ws

    @property
    def state(self) -> Literal['X'] | Literal['O']:
        return self.__state

    @property
    def ws(self) -> WebSocket:
        return self.__ws

    @property
    def username(self) -> str:
        return self.__username


class Game:
    winning_conditions: Tuple[tuple] = (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6)
    )

    __number: int = 0
    player_1: Player | None = None
    player_2: Player | None = None
    current_player: Player | str = ''
    active_game: bool = False
    __won = False
    __draw = False

    def __init__(self, number):
        self.__number = number
        self.game_state = ["", "", "", "", "", "", "", "", ""]

    async def start(self, ws: WebSocket, user: User) -> None:
        player = self.create_player(ws, 'X', user.display_name)
        self.player_1 = player
        self.current_player = player

    async def join_player(self, ws: WebSocket, user: User) -> None | bool:
        player = self.create_player(ws, 'O', user.display_name)
        if player != self.player_1 and self.player_2 is None:
            self.player_2 = player
            self.active_game = True
            return True

    def create_player(self, ws: WebSocket, state: Literal['X', 'O'], username: str) -> Player:
        return Player(ws, state, username)

    async def check_player_ws(self, ws: WebSocket) -> bool:
        is_ws = False
        if self.player_1 is not None:
            is_ws = self.player_1.check_ws(ws)
        if not is_ws and self.player_2 is not None:
            is_ws = self.player_2.check_ws(ws)
        return is_ws

    def result_validation(self) -> str:
        for i in self.winning_conditions:
            a = self.game_state[i[0]]
            b = self.game_state[i[1]]
            c = self.game_state[i[2]]

            if a == "" and b == "" and c == "":
                continue

            if a == b and b == c:
                self.__won = True
                break

        if self.__won:
            self.active_game = False
            return self.winning_message()

        if "" not in self.game_state:
            self.active_game = False
            self.__draw = True
            return self.draw_message()

        self.change_current_player()

        return self.move_message()

    def cell_played(self, cell_index) -> MoveGame:
        self.game_state[cell_index] = self.current_player.state
        _state = self.current_player.state,
        _message = self.result_validation()
        _player_won = None
        _player_loss = None
        if self.__won:
            _player_won = self.current_player.username
            if self.current_player != self.player_1:
                _player_loss = self.player_1.username
            else:
                _player_loss = self.player_2.username

        return MoveGame(
            _state,
            _message,
            self.active_game,
            self.__won,
            self.__draw,
            _player_won,
            _player_loss
        )

    def change_current_player(self) -> None:
        self.current_player = self.player_1 if self.current_player != self.player_1 else self.player_2

    def winning_message(self) -> str:
        return f"Player {self.current_player.state} won!"

    def draw_message(self) -> str:
        return f"Draw!!!"

    def move_message(self) -> str:
        return f"Player turn {self.current_player.state}"

    @property
    def number(self) -> int:
        return self.__number
