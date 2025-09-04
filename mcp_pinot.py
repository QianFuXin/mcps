from mcp.server.fastmcp import FastMCP
from pinotdb import connect
import requests
from requests.auth import HTTPBasicAuth
from typing import Any, List, Dict

mcp = FastMCP("PinotMCP", port=8004)

BROKER_CONFIG = {
    "host": "localhost",
    "port": 8099,
    "path": "/query/sql",
    "scheme": "http",
    "username": "admin",
    "password": "secret",
}

# Pinot Controller 配置
CONTROLLER_CONFIG = {
    "host": "localhost",
    "port": 9000,
    "scheme": "http",
    "username": "admin",
    "password": "secret",
}


def run_query(sql: str) -> List[Dict[str, Any]]:
    """执行 Pinot SQL 并返回结果"""
    conn = connect(**BROKER_CONFIG)
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


class PinotControllerClient:
    def __init__(self, host, port, scheme, username=None, password=None):
        self.base_url = f"{scheme}://{host}:{port}"
        self.auth = HTTPBasicAuth(username, password) if username and password else None

    def get(self, path: str):
        url = f"{self.base_url}{path}"
        resp = requests.get(url, auth=self.auth)
        resp.raise_for_status()
        return resp.json()

    def list_tables(self):
        return self.get("/tables").get("tables", [])

    def get_table_config(self, table_name: str):
        return self.get(f"/tables/{table_name}")

    def get_table_size(self, table_name: str):
        return self.get(f"/tables/{table_name}/size")

    def list_segments(self, table_name: str):
        return self.get(f"/segments/{table_name}").get("segments", [])

    def get_segment_metadata(self, table_name: str):
        return self.get(f"/segments/{table_name}/metadata")

    def get_schema(self, schema_name: str):
        return self.get(f"/schemas/{schema_name}")


controller = PinotControllerClient(**CONTROLLER_CONFIG)


@mcp.tool()
def execute_sql(sql: str) -> List[Dict[str, Any]]:
    """
    执行 Pinot SQL 语句（SELECT / DML）。
    返回查询结果（列表[dict]）
    """
    return run_query(sql)


@mcp.tool()
def list_tables() -> List[str]:
    """获取所有表名"""
    return controller.list_tables()


@mcp.tool()
def get_table_config(table_name: str) -> Dict[str, Any]:
    """获取表的详细配置信息"""
    return controller.get_table_config(table_name)


@mcp.tool()
def get_table_size(table_name: str) -> Dict[str, Any]:
    """获取表的大小信息"""
    return controller.get_table_size(table_name)


@mcp.tool()
def list_segments(table_name: str) -> List[str]:
    """获取表的 segment 列表"""
    return controller.list_segments(table_name)


@mcp.tool()
def get_segment_metadata(table_name: str) -> Dict[str, Any]:
    """获取表的 segment 元数据"""
    return controller.get_segment_metadata(table_name)


@mcp.tool()
def get_schema(schema_name: str) -> Dict[str, Any]:
    """获取 schema 信息"""
    return controller.get_schema(schema_name)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
