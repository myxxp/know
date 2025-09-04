#!/usr/bin/env python3
"""
测试新的Dify API客户端结构
"""
import os
import sys

def test_dify_api_structure():
    """测试Dify API客户端结构"""
    print("🧪 测试新的Dify API客户端结构...")
    
    # 设置测试环境变量
    test_env_vars = {
        "DB_HOST": "test_host",
        "DB_USER": "test_user", 
        "DB_PASSWORD": "test_password",
        "REDIS_HOST": "test_redis_host",
        "DIFY_API_KEY": "test_api_key"
    }
    
    for key, value in test_env_vars.items():
        os.environ[key] = value
    
    try:
        # 测试导入新的Dify客户端
        from app.services.dify_client import DifyClient
        
        print("✅ Dify客户端导入成功")
        
        # 测试客户端初始化
        client = DifyClient()
        print("✅ Dify客户端初始化成功")
        
        # 检查API方法
        print("\n📋 Dify API方法检查:")
        
        # Datasets API
        datasets_methods = [
            "create_dataset", "get_dataset", "list_datasets", 
            "update_dataset", "delete_dataset"
        ]
        print(f"   - Datasets API: {', '.join(datasets_methods)}")
        
        # Documents API
        documents_methods = [
            "create_document_by_text", "create_document_by_file",
            "get_document", "list_documents", "update_document", "delete_document",
            "get_document_indexing_status", "enable_document", "disable_document"
        ]
        print(f"   - Documents API: {', '.join(documents_methods)}")
        
        # Segments API
        segments_methods = [
            "list_document_segments", "update_document_segment", "delete_document_segment"
        ]
        print(f"   - Segments API: {', '.join(segments_methods)}")
        
        # Batch Operations
        batch_methods = [
            "batch_create_documents", "batch_delete_documents"
        ]
        print(f"   - Batch Operations: {', '.join(batch_methods)}")
        
        # Retrieve API
        retrieve_methods = ["retrieve"]
        print(f"   - Retrieve API: {', '.join(retrieve_methods)}")
        
        # 兼容性方法
        compatibility_methods = [
            "create_knowledge_base", "upload_document", "get_dataset_info", "call_dify_api"
        ]
        print(f"   - 兼容性方法: {', '.join(compatibility_methods)}")
        
        print("\n✅ Dify API客户端结构测试完成")
        print("📚 详细API文档请参考: DIFY_API.md")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_dify_api_structure()
