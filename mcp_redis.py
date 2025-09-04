from mcp.server.fastmcp import FastMCP
import redis
from typing import Any, List

mcp = FastMCP("RedisMCP", port=8002)

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "password": None,
    "db": 0,
    "decode_responses": True,
    "socket_connect_timeout": 5,
    "socket_timeout": 5,
}


def get_client() -> redis.Redis:
    """获取 Redis 客户端"""
    return redis.Redis(**REDIS_CONFIG)


@mcp.tool()
def execute_command(command: str, *args: str) -> Any:
    """
    执行任意 Redis 命令。
    示例：
    - execute_command("SET", "foo", "bar")
    - execute_command("GET", "foo")
    - execute_command("DEL", "foo")
    """
    client = get_client()
    try:
        return client.execute_command(command, *args)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_value(key: str) -> Any:
    """获取指定 key 的值"""
    client = get_client()
    return client.get(key)


@mcp.tool()
def set_value(key: str, value: str, expire: int = 0) -> bool:
    """
    设置 key 的值，可以指定过期时间（秒）
    """
    client = get_client()
    if expire > 0:
        return client.set(key, value, ex=expire)
    return client.set(key, value)


@mcp.tool()
def delete_key(key: str) -> int:
    """删除指定 key，返回删除的数量"""
    client = get_client()
    return client.delete(key)


@mcp.tool()
def list_keys(pattern: str = "*") -> List[str]:
    """列出所有匹配的 key（默认所有 key）"""
    client = get_client()
    return client.keys(pattern)


@mcp.tool()
def db_size() -> int:
    """返回当前数据库的 key 总数"""
    client = get_client()
    return client.dbsize()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
