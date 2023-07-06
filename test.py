import asyncio


def my_async_function():
    print("Async function started")
    asyncio.sleep(1)  # 模拟一个耗时的操作
    print("Async function resumed")


# 创建一个事件循环
loop = asyncio.get_event_loop()

# 在事件循环中运行异步函数
loop.run_until_complete(my_async_function())

# 关闭事件循环
loop.close()
