from fastapi import APIRouter
import asyncio
import random

def get_create_order_router(manager, orders_db):
    router = APIRouter()
    current_order_id = 1

    async def random_delay():
        await asyncio.sleep(random.uniform(0.1, 1.0))

    @router.post("/orders")
    async def create_order():
        nonlocal current_order_id
        await random_delay()

        new_order = {
            "id": current_order_id,
            "status": "PENDING",
            "created_at": "2024-10-24"
        }
        orders_db[current_order_id] = new_order
        current_order_id += 1

        asyncio.create_task(update_order_status(new_order['id']))
        return {"orderId": new_order["id"], "orderStatus": new_order["status"]}

    async def update_order_status(order_id):
        await asyncio.sleep(random.uniform(0.5, 3.0))
        order = orders_db.get(order_id)
        if order and order["status"] == "PENDING":
            order["status"] = "EXECUTED"
            await manager.broadcast_connections(f"Order {order_id} status changed to EXECUTED")

    return router