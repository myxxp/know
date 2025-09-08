import asyncio
import json
from typing import Callable, Awaitable, Dict, Any, List

from app.dify.dify_client import DifyHttpClient
from app.dify.dify_knowledge_base import DifyKnowledgeBase
from app.services.dify_kb_service import DifyKnowledgeBaseService

OUTPUT_FILE = "dify_responses.json"
results: List[Dict[str, Any]] = []  # 所有测试结果将追加到这里


def write_response(label: str, data: Dict[str, Any]):
    results.append({"label": label, "data": data})


async def test_create_dataset(kb: DifyKnowledgeBase):
    result = await kb.create_dataset(
        name="test", permission="only_me", indexing_technique="high_quality"
    )
    write_response("create_dataset", result)


async def test_list_datasets(kb: DifyKnowledgeBase):
    result = await kb.list_datasets(page=1, limit=20)
    write_response("list_datasets", result)


async def test_get_dataset(kb: DifyKnowledgeBase):
    result = await kb.get_dataset(dataset_id="8c49a7d1-c384-4270-99ee-385e4514aae8")
    write_response("get_dataset", result)


async def test_update_dataset(kb: DifyKnowledgeBase):
    result = await kb.update_dataset(dataset_id="8c49a7d1-c384-4270-99ee-385e4514aae8", data={"name": "test-22"})
    write_response("update_dataset", result)


async def test_create_document_by_file(kb: DifyKnowledgeBase):
    result = await kb.create_document_by_file(dataset_id="8c49a7d1-c384-4270-99ee-385e4514aae8", file_path="/Users/crab/project/knowleage/app/dify/files/test.pdf")
    write_response("create_document_by_file", result)


async def test_list_documents_by_dataset_id(kb: DifyKnowledgeBase):
    result = await kb.list_documents_by_dataset_id(dataset_id="8c49a7d1-c384-4270-99ee-385e4514aae8")
    write_response("list_documents_by_dataset_id", result)

async def test_get_document_by_id(kb: DifyKnowledgeBase):
    result = await kb.get_document_by_id(dataset_id="8c49a7d1-c384-4270-99ee-385e4514aae8", document_id="8c49a7d1-c384-4270-99ee-385e4514aae8")
    write_response("get_document_by_id", result)

async def test_add_document_metadata(kb: DifyKnowledgeBase):
    metadata = [
        {"name": "test", "value": "test"},
        {"name": "test2", "value": "test2"},
    ]
    result = await kb.add_document_metadata(dataset_id="8c49a7d1-c384-4270-99ee-385e4514aae8", metadata=metadata)
    write_response("add_document_metadata", result)


async def test_add_dataset_metadata(dify_service: DifyKnowledgeBaseService):
    metadata = {"test5": "test5", "test6": "test6"}
    result = await dify_service.create_dataset_metadata(dataset_id="8c49a7d1-c384-4270-99ee-385e4514aae8", metadata=metadata)
    write_response("add_dataset_metadata", result)

async def test_list_dataset_metadata(kb: DifyKnowledgeBase):
    result = await kb.list_dataset_metadata(dataset_id="8c49a7d1-c384-4270-99ee-385e4514aae8")
    write_response("list_dataset_metadata", result)

async def test_create_document_by_file_save_doc_id(dify_service: DifyKnowledgeBaseService):
    result = await dify_service.create_document_by_file_save_doc_id(dataset_id="8c49a7d1-c384-4270-99ee-385e4514aae8", file_path="/Users/crab/project/knowleage/app/dify/files/test.pdf")
    write_response("create_document_by_file_save_doc_id", result)

async def main():
    client = DifyHttpClient(
        base_url="https://api.dify.ai",
        api_key="dataset-w10C4Wxt4sf8AkOGok4L26NK"
    )
    kb = DifyKnowledgeBase(client)
    dify_service = DifyKnowledgeBaseService(kb)

# ✅ 第一批：测试 DifyKnowledgeBase（中间层）
    test_kb_tasks: list[Callable[[DifyKnowledgeBase], Awaitable[None]]] = [
        
        
        # 更多测试函数...
    ]

    # ✅ 第二批：测试 DifyKnowledgeBaseService（上层业务封装）
    test_service_tasks: list[Callable[[DifyKnowledgeBaseService], Awaitable[None]]] = [
        test_create_document_by_file_save_doc_id
        # 更多测试函数...
    ]

    # ✅ 运行第一批测试
    print("====== 开始运行 DifyKnowledgeBase 测试 ======")
    for test_fn in test_kb_tasks:
        try:
            await test_fn(kb)
        except Exception as e:
            print(f"❌ 测试失败: {test_fn.__name__} -> {str(e)}")

    # ✅ 运行第二批测试
    print("====== 开始运行 DifyKnowledgeBaseService 测试 ======")
    for test_fn in test_service_tasks:
        try:
            await test_fn(dify_service)
        except Exception as e:
            print(f"❌ 测试失败: {test_fn.__name__} -> {str(e)}")

    await client.close()

    # ✅ 将所有结果格式化写入 JSON 文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n📦 所有响应已写入 {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
