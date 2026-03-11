#!/usr/bin/env python3
"""初始化数据库表结构"""

import asyncio
from src.app.core.database import Base, engine
from src.app.features.users.models import User
from src.app.features.reports.models import Report
from src.app.features.orders.models import Order


async def init_db():
    """创建所有数据库表"""
    async with engine.begin() as conn:
        # 删除所有现有表
        await conn.run_sync(Base.metadata.drop_all)
        # 创建所有新表
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表结构创建成功！")


if __name__ == "__main__":
    asyncio.run(init_db())
