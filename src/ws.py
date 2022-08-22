from typing import List, Any
from starlette.websockets import WebSocket

from .services import GameService
from .ws_classes import WebSocketBroadcast


class WSGame(WebSocketBroadcast):
    actions: List[str] = ['create', 'join', 'new', 'close', 'move']
    service = GameService()

    async def new(self, websocket: WebSocket, data: Any) -> None:
        await websocket.send_json({'action': 'new', 'games': list(self.service.games.keys())})

    async def create(self, websocket: WebSocket, data: Any) -> None:
        game = await self.service.create_game(websocket)
        await websocket.send_json({
            'action': 'create',
            'player': await game.player_1.get_state(),
            'number': game.number
        })
        await self.manager.broadcast({'action': 'new', 'games': list(self.service.games.keys())})

    async def join(self, websocket: WebSocket, data: Any):
        if game := await self.service.join_game(websocket, int(data['game'])):
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

            await self.manager.broadcast({'action': 'new', 'games': list(self.service.games.keys())})
        else:
            await websocket.send_json({'action': 'error', 'message': 'The game has been started'})

    async def move(self, websocket: WebSocket, data: Any):
        game = await self.service.move_game(websocket, data['cell'], int(data['number']))
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
        if players_ws := await self.service.delete_game(websocket):
            for ws in players_ws:
                if ws is not None:
                    await ws.send_json({'action': 'close', 'games': list(self.service.games.keys())})

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await self.close(websocket, close_code)
        await super().on_disconnect(websocket, close_code)
