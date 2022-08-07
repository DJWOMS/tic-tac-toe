import typing

from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from .game import Game


class WebSocketActions(WebSocketEndpoint):
    encoding = 'json'
    actions = []
    async def actions_not_allowed(self, websocket: WebSocket, data: typing.Any):
        await websocket.send_json({'action': 'Not found'})

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:
        if data['action'] in self.actions:
            handler = getattr(self, data['action'], self.actions_not_allowed)
        else:
            handler = self.actions_not_allowed
        return await handler(websocket, data)


class WSGame(WebSocketActions):
    actions = ['create', 'join', 'new', 'close', 'move']
    users = []
    games = []
    current_games = []

    async def create_game(self, ws: WebSocket) -> Game:
        game = await Game.create(ws)
        self.games.append(game)
        return game

    async def join_game(self, ws: WebSocket, number: int) -> Game:
        game = self.games.pop(number - 1)
        self.current_games.append(game)
        await game.join_player(ws)
        return game

    async def get_current_game(self, ws: WebSocket) -> Game:
        for game in self.current_games:
            if await game.check_player_ws(ws):
                return game

    async def get_game(self, ws: WebSocket) -> Game:
        for game in self.current_games:
            if await game.check_player_ws(ws):
                return game
        for game in self.games:
            if await game.check_player_ws(ws):
                return game

    async def move_game(self, ws: WebSocket, cell: int) -> tuple:
        game = await self.get_current_game(ws)
        state, message = await game.cell_played(cell)
        return (
            state,
            message,
            await game.player_1.get_ws(),
            await game.player_2.get_ws()
        )

    async def delete_game(self, ws: WebSocket) -> tuple:
        game = await self.get_game(ws)
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

    async def add_user(self, ws: WebSocket) -> None:
        self.users.append(ws)

    async def delete_user(self, ws: WebSocket):
        self.users.remove(ws)

    async def on_connect(self, websocket: WebSocket) -> None:
        await self.add_user(websocket)
        await websocket.accept()

    async def new(self, websocket: WebSocket, data: typing.Any):
        await websocket.send_json({'action': 'new', 'games': len(self.games)})

    async def create(self, websocket: WebSocket, data: typing.Any):
        game = await self.create_game(websocket)
        await websocket.send_json(
            {'action': 'create', 'player': await game.player_1.get_state()}
        )
        await self.delete_user(websocket)
        for ws in self.users:
            await ws.send_json({'action': 'new', 'games': len(self.games)})

    async def join(self, websocket: WebSocket, data: typing.Any):
        game = await self.join_game(websocket, int(data['game']))
        await self.delete_user(websocket)
        await websocket.send_json(
            {
                'action': 'join',
                'other_player': await game.player_1.get_state(),
                'player': await game.player_2.get_state(),
                'move': False
            }
        )
        ws = await game.player_1.get_ws()
        await ws.send_json(
            {
                'action': 'join',
                'other_player': await game.player_2.get_state(),
                'player': await game.player_1.get_state(),
                'move': True
            }
        )

        for ws in self.users:
            await ws.send_json({'action': 'new', 'games': len(self.games)})

    async def move(self, websocket: WebSocket, data: typing.Any):
        state, message, ws1, ws2 = await self.move_game(websocket, data['cell'])
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

    async def close(self, websocket: WebSocket, data: typing.Any):
        await self.add_user(websocket)
        players_ws = await self.delete_game(websocket)
        for ws in players_ws:
            if ws is not None:
                await ws.send_json({'action': 'new', 'games': len(self.games)})

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        pass
