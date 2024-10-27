from fastapi import APIRouter, HTTPException
import asyncio
import random

def get_cancel_order_router(manager, orders_db):
    router = APIRouter()

    async def random_delay():
        await asyncio.sleep(random.uniform(0.1, 1.0))

    @router.delete("/orders/{order_id}")
    async def cancel_order(order_id: int):
        await random_delay()
        order = orders_db.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order["status"] != "PENDING":
            raise HTTPException(status_code=400, detail="Order cannot be canceled")
        order["status"] = "CANCELLED"

        await manager.broadcast_connections(f"Order {order_id} status changed to CANCELLED")
        return {"message": f"Order {order_id} cancelled"}

    return router