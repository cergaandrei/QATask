# requests_to_validate/specific_order.py
from fastapi import APIRouter, HTTPException
import asyncio
import random

def get_specific_order_router(orders_db):
    router = APIRouter()

    async def random_delay():
        await asyncio.sleep(random.uniform(0.1, 1.0))

    @router.get("/orders/{order_id}")
    async def get_order(order_id: int):
        await random_delay()
        order = orders_db.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    return router
