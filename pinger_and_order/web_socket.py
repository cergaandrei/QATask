class Connect_Clients:
    def __init__(self):
        self.connections = []
        self.orders_db = {}
    async def connect_connections(self, websocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect_connections(self, websocket):
        self.connections.remove(websocket)

    async def broadcast_connections(self, message):
        for connection in self.connections:
            await connection.send_text(message)
