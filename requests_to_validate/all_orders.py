from fastapi import APIRouter
import asyncio
import random

def get_all_orders_router(orders_db):
    router = APIRouter()

    async def random_delay():
        await asyncio.sleep(random.uniform(0.1, 1.0))

    @router.get("/orders")
    async def get_orders():
        await random_delay()
        return list(orders_db.values())  # Access orders_db directly

    return router
