from app.dify.dify_knowledge_base import DifyKnowledgeBase
from app.dify.dify_client import DifyHttpClient
import asyncio
import sys
import os

from app.services.dify_kb_service import DifyKnowledgeBaseService
from app.utils.utils import save_doc_id

from app.services.database_service import DatabaseService


async def main():
    dify_kb = DifyKnowledgeBase()
    dify_service = DifyKnowledgeBaseService()
    db_service = DatabaseService()

    #1.查询MySQL数据库
    task_id = ""
    target_id = ""
    sql = ""
    result = db_service.query_data(sql)
    for item in result:
        task_id = item.workflow_id
        target_id = item.id
        #2.查询




asyncio.run(main())
