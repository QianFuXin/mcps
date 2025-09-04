from mcp.server.fastmcp import FastMCP
from typing import Any, List, Dict
from pymongo import MongoClient

mcp = FastMCP("MongoMCP", port=8003)

MONGO_CONFIG = {
    "host": "localhost",
    "port": 27017,
    "username": None,
    "password": None,
    "authSource": "admin",
}
DEFAULT_DB = "spring_demo"


def get_client() -> MongoClient:
    """获取 MongoDB 客户端"""
    return MongoClient(**{k: v for k, v in MONGO_CONFIG.items() if v is not None})


@mcp.tool()
def list_collections(database: str = DEFAULT_DB) -> List[str]:
    """获取指定数据库中的所有集合名称"""
    client = get_client()
    db = client[database]
    return db.list_collection_names()


@mcp.tool()
def find_documents(
        collection: str,
        query: Dict[str, Any] = {},
        projection: Dict[str, int] = None,
        limit: int = 10,
        database: str = DEFAULT_DB,
) -> List[Dict[str, Any]]:
    """
    查询文档。
    - query: MongoDB 查询条件
    - projection: 指定返回字段，例如 {"_id": 0, "name": 1}
    - limit: 限制返回条数
    """
    client = get_client()
    db = client[database]
    cursor = db[collection].find(query, projection, limit=limit)
    return list(cursor)


@mcp.tool()
def insert_document(collection: str, document: Dict[str, Any], database: str = DEFAULT_DB) -> str:
    """插入一个文档，返回新文档的 _id"""
    client = get_client()
    db = client[database]
    result = db[collection].insert_one(document)
    return str(result.inserted_id)


@mcp.tool()
def update_documents(
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        many: bool = False,
        database: str = DEFAULT_DB,
) -> Dict[str, int]:
    """
    更新文档。
    - query: 查询条件
    - update: 更新操作，例如 {"$set": {"age": 30}}
    - many: 是否更新多个
    """
    client = get_client()
    db = client[database]
    if many:
        result = db[collection].update_many(query, update)
    else:
        result = db[collection].update_one(query, update)
    return {"matched": result.matched_count, "modified": result.modified_count}


@mcp.tool()
def delete_documents(
        collection: str,
        query: Dict[str, Any],
        many: bool = False,
        database: str = DEFAULT_DB,
) -> Dict[str, int]:
    """删除文档，返回删除数量"""
    client = get_client()
    db = client[database]
    if many:
        result = db[collection].delete_many(query)
    else:
        result = db[collection].delete_one(query)
    return {"deleted": result.deleted_count}


@mcp.tool()
def collection_count(collection: str, database: str = DEFAULT_DB) -> int:
    """统计集合中文档数量"""
    client = get_client()
    db = client[database]
    return db[collection].count_documents({})


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
