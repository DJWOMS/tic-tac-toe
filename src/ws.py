from typing import List, Any

from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from .game import Game


class WebSocketManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await self.add_connection(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        await self.delete_connection(websocket)

    async def add_connection(self, websocket: WebSocket) -> None:
        self.connections.append(websocket)

    async def delete_connection(self, websocket: WebSocket) -> None:
        self.connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: dict) -> None:
        await websocket.send_json(message)

    async def broadcast(self, message: dict) -> None:
        for connection in self.connections:
            await connection.send_json(message)


class WebSocketActions(WebSocketEndpoint):
    encoding = 'json'
    actions: List[str] = []

    async def actions_not_allowed(self, websocket: WebSocket, data: Any) -> None:
        await websocket.send_json({'action': 'Not found'})

    async def on_receive(self, websocket: WebSocket, data: Any):
        if data['action'] in self.actions:
            handler = getattr(self, data['action'], self.actions_not_allowed)
        else:
            handler = self.actions_not_allowed
        return await handler(websocket, data)


class WebSocketBroadcast(WebSocketActions):
    manager = WebSocketManager()

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await self.manager.connect(websocket)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await self.manager.disconnect(websocket)


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

    async def get_current_game(self, number: int, ws: WebSocket) -> Game:
        try:
            game = self.current_games[number]
        except IndexError:
            await self.manager.disconnect(ws)
        else:
            if await game.check_player_ws(ws):
                return game

    async def get_game(self, ws: WebSocket) -> Game:
        for game in self.current_games:
            if await game.check_player_ws(ws):
                return game
        for game in self.games:
            if await game.check_player_ws(ws):
                return game

    async def move_game(self, ws: WebSocket, cell: int, number: int) -> tuple:
        game = await self.get_current_game(number, ws)
        if game is not None:
            state, message = await game.cell_played(cell)
            return (
                state,
                message,
                await game.player_1.get_ws(),
                await game.player_2.get_ws()
            )
        await self.close(ws)

    async def delete_game(self, ws: WebSocket) -> tuple:
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
            return pl1, pl2

    async def new(self, websocket: WebSocket, data: Any):
        await websocket.send_json({'action': 'new', 'games': len(self.games)})

    async def create(self, websocket: WebSocket, data: Any):
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
        state, message, ws1, ws2 = await self.move_game(websocket, data['cell'], data['number'])
        await ws1.send_json(
            {
                'action': 'move',
                'cell': data['cell'],
                'move': True if websocket != ws1 else False,
                'state': state,
                'message': message
            }
        )
        await ws2.send_json(
            {
                'action': 'move',
                'cell': data['cell'],
                'move': True if websocket != ws2 else False,
                'state': state,
                'message': message
            }
        )

    async def close(self, websocket: WebSocket):
        players_ws = await self.delete_game(websocket)
        if players_ws is not None:
            for ws in players_ws:
                if ws is not None:
                    await ws.send_json({'action': 'close', 'games': len(self.games)})

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await super().on_disconnect(websocket, close_code)
        await self.close(websocket)
