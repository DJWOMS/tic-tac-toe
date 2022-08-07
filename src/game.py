from starlette.websockets import WebSocket


class Player:

    def __init__(self, ws: WebSocket, state: str = 'X') -> None:
        self.__ws = ws
        self.__state = state

    async def get_state(self):
        return self.__state

    async def get_ws(self):
        return self.__ws

    async def check_ws(self, ws: WebSocket) -> bool:
        return ws == self.__ws


class Game:

    winning_conditions = (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6)
    )
    game_state = ["", "", "", "", "", "", "", "", ""]

    player_1 = None
    player_2 = None
    current_player = ''
    active_game = False

    @classmethod
    async def create(cls, ws: WebSocket):
        self = cls()
        player = await self.create_player(ws)
        self.player_1 = player
        self.current_player = await player.get_state()
        return self

    async def create_player(self, ws: WebSocket):
        return Player(ws, 'X')

    async def join_player(self, ws: WebSocket):
        player = Player(ws, 'O')
        if player != self.player_1 and player != self.player_2:
            self.player_2 = player
            self.active_game = True

    async def check_player_ws(self, ws: WebSocket) -> bool:
        if await self.player_1.check_ws(ws) or await self.player_2.check_ws(ws):
            return True
        return False

    async def result_validation(self) -> str:
        won = False

        for i in self.winning_conditions:
            a = self.game_state[i[0]]
            b = self.game_state[i[1]]
            c = self.game_state[i[2]]

            if a == "" and b == "" and c == "":
                continue

            if a == b and b == c:
                won = True
                break

        if won:
            self.active_game = False
            return await self.winning_message()

        if "" not in self.game_state:
            self.active_game = False
            return await self.draw_message()

        await self.change_current_player()

        return await self.move_message()

    async def cell_played(self, cell_index) -> tuple:
        self.game_state[cell_index] = self.current_player
        return self.current_player, await self.result_validation()

    async def change_current_player(self):
        self.current_player = "X" if self.current_player != "X" else "O"

    async def winning_message(self):
        return f"Победил игрок {self.current_player}"

    async def draw_message(self):
        return f"Ничья!!!"

    async def move_message(self):
        return f"Ход игрока {self.current_player}"








