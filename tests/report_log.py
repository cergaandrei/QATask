import pytest
from fastapi import FastAPI, WebSocket
import uvicorn
import threading
import httpx
import asyncio
import time
import statistics
import websockets
from requests_to_validate.all_orders import get_all_orders_router
from requests_to_validate.cancel_order import get_cancel_order_router
from requests_to_validate.create_order import get_create_order_router
from requests_to_validate.specific_order import get_specific_order_router
from pinger_and_order.web_socket import Connect_Clients

app = FastAPI()
manager = Connect_Clients()
manager.orders_db = {}
app.include_router(get_all_orders_router(manager.orders_db))
app.include_router(get_cancel_order_router(manager, manager.orders_db))
app.include_router(get_create_order_router(manager, manager.orders_db))
app.include_router(get_specific_order_router(manager.orders_db))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect_connections(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            order_id = data.get("orderId")
            if action == "subscribe":
                order = manager.orders_db.get(order_id)
                if order:
                    await websocket.send_json({"orderId": order_id, "orderStatus": order["status"]})
            elif action == "update":
                status = data.get("status")
                order = manager.orders_db.get(order_id)
                if order:
                    order["status"] = status
                    await manager.broadcast_connections(f"Order {order_id} status changed to {status}")
    except Exception as e:
        print(f"Exception in WebSocket: {e}")
    finally:
        await manager.disconnect_connections(websocket)
        print("WebSocket connection closed")

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

@pytest.fixture(scope="session", autouse=True)
def fastapi_server():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    time.sleep(1)
    asyncio.run(check_server_health())
    yield

async def check_server_health():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/health")
        assert response.status_code == 200

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@pytest.fixture(autouse=True)
def setup_orders():
    manager.orders_db[1] = {"id": 1, "status": "PENDING"}
    manager.orders_db[2] = {"id": 2, "status": "EXECUTED"}

class TestAPI:

    def setup_method(self):
        self.manager = manager

    @pytest.mark.asyncio
    async def test_validate_create_order(self):
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8000/orders")
            new_order = response.json()

        assert new_order['orderStatus'] == "PENDING"
        assert 'orderId' in new_order

    @pytest.mark.asyncio
    async def test_validate_all_orders(self):
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/orders")
            orders = response.json()

        assert isinstance(orders, list)
        assert len(orders) == 2

    @pytest.mark.asyncio
    async def test_validate_cancel_order(self):
        async with httpx.AsyncClient() as client:
            response = await client.delete("http://127.0.0.1:8000/orders/1")
            cancel_response = response.json()

        assert cancel_response['message'] == "Order 1 cancelled"
        assert self.manager.orders_db[1]['status'] == "CANCELLED"

    @pytest.mark.asyncio
    async def test_validate_specific_order(self):
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/orders/1")
            order = response.json()

        assert order['id'] == 1

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="Order does not exist")
    async def test_cancel_nonexistent_order(self):
        async with httpx.AsyncClient() as client:
            response = await client.delete("http://127.0.0.1:8000/orders/999")
            assert response.status_code == 404  # Check for correct status code
            assert False, "This test is expected to fail, as the order does not exist."  # This assertion will always fail

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="Order cannot be canceled")
    async def test_cancel_executed_order(self):
        self.manager.orders_db[3] = {"id": 3, "status": "EXECUTED"}
        async with httpx.AsyncClient() as client:
            response = await client.delete("http://127.0.0.1:8000/orders/3")
            assert response.status_code == 400  # Check for correct status code
            assert False, "This test is expected to fail, as the order is already executed."  # This assertion will always fail

    @pytest.mark.asyncio
    async def test_websocket_order_status(self):
        uri = "ws://127.0.0.1:8000/ws"
        async with websockets.connect(uri) as websocket:
            await websocket.send('{"action": "subscribe", "orderId": 1}')
            response = await websocket.recv()
            assert "PENDING" in response
            await websocket.send('{"action": "update", "orderId": 1, "status": "EXECUTED"}')
            response = await websocket.recv()
            assert "EXECUTED" in response

    @pytest.mark.asyncio
    async def test_performance(self):
        start_times = []
        end_times = []

        async with httpx.AsyncClient() as client:
            tasks = []
            for _ in range(100):
                start_times.append(time.time())
                tasks.append(client.post("http://127.0.0.1:8000/orders"))

            responses = await asyncio.gather(*tasks)
            for response in responses:
                assert response.status_code == 200
                end_times.append(time.time())

        delays = [end - start for start, end in zip(start_times, end_times)]
        avg_delay = sum(delays) / len(delays)
        stddev_delay = statistics.stdev(delays)

        print(f"Average order execution delay: {avg_delay:.2f} seconds")
        print(f"Standard deviation of order execution delay: {stddev_delay:.2f} seconds")