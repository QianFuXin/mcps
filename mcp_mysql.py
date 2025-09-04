from mcp.server.fastmcp import FastMCP
import pymysql
from typing import Any, List, Dict

mcp = FastMCP("MysqlMCP", port=8001)

# 数据库连接配置（建议改成从环境变量读取）
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "xxx",
    "database": "xxx",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
    "connect_timeout": 5,
    "read_timeout": 10,
    "write_timeout": 10,
}


def run_query(sql: str, params: tuple = ()) -> Any:
    """执行 SQL 并返回结果"""
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            if cursor.description:
                return cursor.fetchall()
            else:
                return {"affected_rows": cursor.rowcount}
    finally:
        connection.close()


@mcp.tool()
def execute_sql(sql: str) -> Any:
    """
    执行 SQL 语句，可以是 SELECT/INSERT/UPDATE/DELETE。
    - SELECT 返回查询结果（列表[dict]）
    - 其他语句返回 {"affected_rows": n}
    """
    return run_query(sql)


@mcp.tool()
def list_tables() -> List[dict]:
    """获取当前数据库中所有表的详细信息（表名、引擎、行数、时间、注释等）"""
    rows = run_query("SHOW TABLE STATUS")
    if not rows:
        return []
    return rows


@mcp.tool()
def describe_table(table_name: str) -> List[Dict[str, Any]]:
    """
    获取指定表的字段信息（字段名、类型、注释、可否为空、主键等）
    """
    return run_query(f"SHOW FULL COLUMNS FROM `{table_name}`")


@mcp.tool()
def table_count(table_name: str) -> int:
    """获取指定表的总行数"""
    rows = run_query(f"SELECT COUNT(*) as cnt FROM `{table_name}`")
    return rows[0]["cnt"] if rows else 0


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
