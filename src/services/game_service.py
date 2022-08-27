from typing import Dict

from starlette.websockets import WebSocket

from src.auth.models import User
from src.auth.service import UserService
from src.game import Game
from src.interfaces import GameState, PlayersWebSocket, GameInterface


class GameService:
    games: Dict[int, Game] = {}
    __number_last_game: int = 1

    async def set_last_game(self, game) -> None:
        self.games[self.__number_last_game] = game
        self.__number_last_game += 1

    async def create_game(self, ws: WebSocket, user: User) -> Game:
        game = Game(self.__number_last_game)
        await game.start(ws, user)
        await self.set_last_game(game)
        return game

    async def join_game(self, ws: WebSocket, number: int, user: User) -> Game | None:
        if game := self.games.get(number):
            if await game.join_player(ws, user):
                return game

    async def get_current_game(self, number: int, ws: WebSocket) -> Game | None:
        if game := self.games.get(number):
            if await game.check_player_ws(ws):
                return game

    async def search_game(self, ws: WebSocket) -> GameInterface | None:
        for k, game in self.games.items():
            if await game.check_player_ws(ws):
                return GameInterface(k, game)

    async def move_game(self, ws: WebSocket, cell: int, number: int) -> GameState | None:
        if current_game := await self.get_current_game(number, ws):
            game = current_game.cell_played(cell)
            if game.is_won:
                await self.set_win(game.player_won, game.player_loss)
            elif game.is_draw:
                await self.set_draw(current_game.player_1.username, current_game.player_2.username)

            return GameState(
                game.is_active,
                game.state,
                game.message,
                current_game.player_1.ws,
                current_game.player_2.ws
            )

    async def delete_game(self, ws: WebSocket) -> PlayersWebSocket | None:
        if current := await self.search_game(ws):
            pl1, pl2 = None, None
            if pl := current.game.player_1:
                pl1 = pl.ws
            if pl := current.game.player_2:
                pl2 = pl.ws
            self.games.pop(current.key)
            return PlayersWebSocket(pl1, pl2)

    async def set_win(self, username_win: str, username_loss: str) -> None:
        user = await UserService.ainit()
        await user.update_user(username_win, win=1)
        await user.update_user(username_loss, loss=1)
        await user.db_session.close()

    async def set_draw(self, username_1: str, username_2: str) -> None:
        user = await UserService.ainit()
        await user.update_user(username_1, draw=1)
        await user.update_user(username_2, draw=1)
        await user.db_session.close()

    async def get_top(self):
        _top_list = []
        top = await UserService.ainit()
        user_list = await top.get_top_users()
        for user in user_list:
            _top_list.append(
                {'name': user.name, 'win': user.win, 'lose': user.loss, 'draw': user.draw}
            )
        return _top_list

    async def get_games(self) -> dict:
        _games = {}
        for k, instance in self.games.items():
            _games[k] = {'creator': instance.player_1.username, 'isActive': instance.active_game}
        return _games
