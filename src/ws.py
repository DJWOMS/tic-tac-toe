from typing import List, Any

from starlette.websockets import WebSocket

from .game import Game
from .interfaces import GameState, PlayersWebSocket
from .ws_classes import WebSocketBroadcast


class WSGame(WebSocketBroadcast):
    actions: List[str] = ['create', 'join', 'new', 'close', 'move']
    games: List[Game] = []
    current_games: List[Game] = []
    __number_last_game: int = 0

    async def set_last_game(self, game) -> None:
        self.games.append(game)
        self.__number_last_game = len(self.games)

    async def create_game(self, ws: WebSocket) -> Game:
        game = await Game.create(ws, self.__number_last_game)
        await self.set_last_game(game)
        return game

    async def join_game(self, ws: WebSocket, number: int) -> Game:
        game = self.games.pop(number)
        self.current_games.append(game)
        await game.join_player(ws)
        return game

    async def get_current_game(self, number: int, ws: WebSocket) -> Game | None:
        try:
            game = self.current_games[number]
        except IndexError:
            await self.manager.disconnect(ws)
        else:
            if await game.check_player_ws(ws):
                return game

    async def get_game(self, ws: WebSocket) -> Game | None:
        for game in self.current_games:
            if await game.check_player_ws(ws):
                return game
        for game in self.games:
            if await game.check_player_ws(ws):
                return game

    async def move_game(self, ws: WebSocket, cell: int, number: int) -> GameState | None:
        game = await self.get_current_game(number, ws)
        if game is not None:
            state, message, is_active = await game.cell_played(cell)
            return GameState(
                is_active,
                state,
                message,
                await game.player_1.get_ws(),
                await game.player_2.get_ws()
            )
        await self.close(ws)

    async def delete_game(self, ws: WebSocket) -> PlayersWebSocket | None:
        game = await self.get_game(ws)
        if game is not None:
            if game in self.current_games:
                self.current_games.remove(game)
            elif game in self.games:
                self.games.remove(game)

            pl1, pl2 = None, None

            if game.player_1 is not None:
                pl1 = await game.player_1.get_ws()
            if game.player_2 is not None:
                pl2 = await game.player_2.get_ws()
            del game
            return PlayersWebSocket(pl1, pl2)

    async def new(self, websocket: WebSocket, data: Any) -> None:
        await websocket.send_json({'action': 'new', 'games': len(self.games)})

    async def create(self, websocket: WebSocket, data: Any) -> None:
        game = await self.create_game(websocket)
        await websocket.send_json({
            'action': 'create',
            'player': await game.player_1.get_state(),
            'number': game.number
        })
        await self.manager.broadcast({'action': 'new', 'games': len(self.games)})

    async def join(self, websocket: WebSocket, data: Any):
        game = await self.join_game(websocket, int(data['game']))
        await websocket.send_json(
            {
                'action': 'join',
                'number': game.number,
                'other_player': await game.player_1.get_state(),
                'player': await game.player_2.get_state(),
                'move': False
            }
        )
        ws = await game.player_1.get_ws()
        await ws.send_json(
            {
                'action': 'join',
                'number': game.number,
                'other_player': await game.player_2.get_state(),
                'player': await game.player_1.get_state(),
                'move': True
            }
        )

        await self.manager.broadcast({'action': 'new', 'games': len(self.games)})

    async def move(self, websocket: WebSocket, data: Any):
        game = await self.move_game(websocket, data['cell'], data['number'])
        _data = {
            'action': 'move',
            'is_active': game.is_active,
            'cell': data['cell'],
            'state': game.state,
            'message': game.message
        }
        _data.update({'move': True if websocket != game.player_ws1 else False})
        await game.player_ws1.send_json(_data)

        _data.update({'move': True if websocket != game.player_ws2 else False})
        await game.player_ws2.send_json(_data)

    async def close(self, websocket: WebSocket, data: Any | None = None) -> None:
        players_ws = await self.delete_game(websocket)
        if players_ws is not None:
            for ws in players_ws:
                if ws is not None:
                    await ws.send_json({'action': 'close', 'games': len(self.games)})

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await self.close(websocket, close_code)
        await super().on_disconnect(websocket, close_code)

