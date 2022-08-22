from typing import List, Any, Dict

from starlette.websockets import WebSocket

from .game import Game
from .interfaces import GameState, PlayersWebSocket, CurrentGame
from .ws_classes import WebSocketBroadcast


class WSGame(WebSocketBroadcast):
    actions: List[str] = ['create', 'join', 'new', 'close', 'move']
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

    async def new(self, websocket: WebSocket, data: Any) -> None:
        await websocket.send_json({'action': 'new', 'games': list(self.games.keys())})

    async def create(self, websocket: WebSocket, data: Any) -> None:
        game = await self.create_game(websocket)
        await websocket.send_json({
            'action': 'create',
            'player': await game.player_1.get_state(),
            'number': game.number
        })
        await self.manager.broadcast({'action': 'new', 'games': list(self.games.keys())})

    async def join(self, websocket: WebSocket, data: Any):
        if game := await self.join_game(websocket, int(data['game'])):
            _data = {
                'action': 'join',
                'number': game.number,
                'other_player': await game.player_1.get_state(),
                'player': await game.player_2.get_state(),
                'move': False
            }
            await websocket.send_json(_data)

            ws = await game.player_1.get_ws()
            _data.update({
                'other_player': await game.player_2.get_state(),
                'player': await game.player_1.get_state(),
                'move': True
            })
            await ws.send_json(_data)

            await self.manager.broadcast({'action': 'new', 'games': list(self.games.keys())})
        else:
            await websocket.send_json({'action': 'error', 'message': 'The game has been started'})

    async def move(self, websocket: WebSocket, data: Any):
        game = await self.move_game(websocket, data['cell'], int(data['number']))
        print('move', game)
        _data = {
            'action': 'move',
            'is_active': game.is_active,
            'cell': data['cell'],
            'state': game.state,
            'message': game.message,
            'move': True if websocket != game.player_ws1 else False
        }
        print('1', _data)
        await game.player_ws1.send_json(_data)

        _data.update({'move': True if websocket != game.player_ws2 else False})
        print('2', _data)
        await game.player_ws2.send_json(_data)

    async def close(self, websocket: WebSocket, data: Any | None = None) -> None:
        if players_ws := await self.delete_game(websocket):
            for ws in players_ws:
                if ws is not None:
                    await ws.send_json({'action': 'close', 'games': list(self.games.keys())})

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await self.close(websocket, close_code)
        await super().on_disconnect(websocket, close_code)
