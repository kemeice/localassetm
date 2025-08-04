from fastapi import APIRouter
import asyncpg
import asyncio

router = APIRouter()

async def get_pool():
    return await asyncpg.create_pool(
        user="admin", password="admin", database="assetdb", host="postgres"
    )

@router.get("/trades")
async def fetch_trades(limit: int = 10):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM trades LIMIT $1", limit)
    return [dict(r) for r in rows]