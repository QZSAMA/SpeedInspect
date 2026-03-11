#!/usr/bin/env python3
"""初始化数据库脚本"""

import asyncio
from src.app.core.database import Base, engine
from src.app.features.users.models import User
from src.app.features.reports.models import Report
from src.app.features.orders.models import Order


async def init_db():
    """创建所有表"""
    print("开始创建数据库表...")
    async with engine.begin() as conn:
        # 删除所有旧表（开发环境使用，生产环境请注释）
        await conn.run_sync(Base.metadata.drop_all)
        # 创建所有新表
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表创建完成！")
    
    # 验证表是否创建成功
    async with engine.connect() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: [table.name for table in Base.metadata.sorted_tables]
        )
        print(f"已创建的表: {tables}")


if __name__ == "__main__":
    asyncio.run(init_db())
