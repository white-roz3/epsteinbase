import asyncpg
import os
from typing import AsyncGenerator

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/epsteinbase")

pool: asyncpg.Pool = None

async def get_pool() -> asyncpg.Pool:
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return pool

async def close_pool():
    global pool
    if pool:
        await pool.close()
        pool = None



