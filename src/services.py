from typing import Dict

from starlette.websockets import WebSocket

from .game import Game
from .interfaces import GameState, PlayersWebSocket, CurrentGame


class GameService:
    games: Dict[int, Game] = {}
    __number_last_game: int = 1

    async def set_last_game(self, game) -> None:
        self.games[self.__number_last_game] = game
        self.__number_last_game += 1

    async def create_game(self, ws: WebSocket) -> Game:
        game = Game(self.__number_last_game)
        await game.start(ws)
        await self.set_last_game(game)
        return game

    async def join_game(self, ws: WebSocket, number: int) -> Game | None:
        if game := self.games.get(number):
            if await game.join_player(ws):
                return game

    async def get_current_game(self, number: int, ws: WebSocket) -> Game | None:
        print(number, ws)
        print(self.games.get(number))
        print(self.games)
        if game := self.games.get(number):
            print('get_current_game', game)
            if await game.check_player_ws(ws):
                return game

    async def get_game(self, ws: WebSocket) -> CurrentGame | None:
        for k, game in self.games.items():
            if await game.check_player_ws(ws):
                return CurrentGame(k, game)

    async def move_game(self, ws: WebSocket, cell: int, number: int) -> GameState | None:
        if game := await self.get_current_game(number, ws):
            print('ggg', game)
            state, message, is_active = await game.cell_played(cell)
            return GameState(
                is_active,
                state,
                message,
                await game.player_1.get_ws(),
                await game.player_2.get_ws()
            )
        print('game move close')
        await self.close(ws)

    async def delete_game(self, ws: WebSocket) -> PlayersWebSocket | None:
        if current := await self.get_game(ws):
            pl1, pl2 = None, None
            if pl := current.game.player_1:
                pl1 = await pl.get_ws()
            if pl := current.game.player_2:
                pl2 = await pl.get_ws()
            self.games.pop(current.key)
            return PlayersWebSocket(pl1, pl2)
