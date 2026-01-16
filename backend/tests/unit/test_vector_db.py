"""
Unit tests for Vector Database

Tests ChromaDB configuration, user isolation, and vector operations.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from backend.app.database.vector_db import (
    VectorDatabase,
    get_vector_db
)
from backend.app.llm.factory import EmbeddingProvider


class TestVectorDatabase:
    """测试向量数据库配置"""
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_init_vector_db(self, mock_embeddings, mock_chroma_client):
        """测试向量数据库初始化"""
        mock_client_instance = MagicMock()
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        
        assert db.client is not None
        assert db.embeddings is not None
        assert db.persist_directory.exists()
        mock_chroma_client.assert_called_once()
        mock_embeddings.assert_called_once_with(provider=EmbeddingProvider.ZHIPUAI_EMBEDDING_3)
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_init_with_custom_directory(self, mock_embeddings, mock_chroma_client):
        """测试使用自定义目录初始化"""
        mock_client_instance = MagicMock()
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        custom_dir = "/tmp/test_chroma_db"
        db = VectorDatabase(persist_directory=custom_dir)
        
        # 比较路径对象而非字符串，避免不同操作系统的路径分隔符差异
        assert db.persist_directory == Path(custom_dir)
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_get_user_collection_new(self, mock_embeddings, mock_chroma_client):
        """测试获取新用户集合"""
        mock_client_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.name = "user_1"
        mock_client_instance.get_collection.side_effect = Exception("Not found")
        mock_client_instance.create_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        collection = db.get_user_collection(user_id=1)
        
        assert collection is not None
        mock_client_instance.create_collection.assert_called_once_with(
            name="user_1",
            metadata={"user_id": 1}
        )
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_get_user_collection_cached(self, mock_embeddings, mock_chroma_client):
        """测试获取缓存的用户集合"""
        mock_client_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.name = "user_1"
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        
        # 第一次获取
        collection1 = db.get_user_collection(user_id=1)
        # 第二次获取（应该从缓存中获取）
        collection2 = db.get_user_collection(user_id=1)
        
        assert collection1 is collection2
        mock_client_instance.get_collection.assert_called_once()


class TestVectorOperations:
    """测试向量操作"""
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_add_documents(self, mock_embeddings, mock_chroma_client):
        """测试添加文档"""
        mock_client_instance = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.get_collection.side_effect = Exception("Not found")
        mock_client_instance.create_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        success = db.add_documents(
            user_id=1,
            documents=["文档1", "文档2"],
            metadatas=[{"source": "test1"}, {"source": "test2"}]
        )
        
        assert success is True
        mock_collection.add.assert_called_once()
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_search_documents(self, mock_embeddings, mock_chroma_client):
        """测试检索文档"""
        mock_client_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["结果1", "结果2"]],
            "metadatas": [[{"source": "test"}]],
            "distances": [[0.1, 0.2]],
            "ids": [["doc1", "doc2"]]
        }
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        results = db.search(user_id=1, query="测试查询", n_results=5)
        
        assert "documents" in results
        assert len(results["documents"]) == 1
        mock_collection.query.assert_called_once()
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_delete_documents(self, mock_embeddings, mock_chroma_client):
        """测试删除文档"""
        mock_client_instance = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        success = db.delete_documents(user_id=1, ids=["doc1", "doc2"])
        
        assert success is True
        mock_collection.delete.assert_called_once_with(ids=["doc1", "doc2"])
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_update_documents(self, mock_embeddings, mock_chroma_client):
        """测试更新文档"""
        mock_client_instance = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        success = db.update_documents(
            user_id=1,
            ids=["doc1"],
            documents=["更新的文档"],
            metadatas=[{"source": "updated"}]
        )
        
        assert success is True
        mock_collection.update.assert_called_once()
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_get_collection_stats(self, mock_embeddings, mock_chroma_client):
        """测试获取集合统计信息"""
        mock_client_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        stats = db.get_collection_stats(user_id=1)
        
        assert stats["user_id"] == 1
        assert stats["count"] == 10
        mock_collection.count.assert_called_once()


class TestCollectionManagement:
    """测试集合管理"""
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_delete_user_collection(self, mock_embeddings, mock_chroma_client):
        """测试删除用户集合"""
        mock_client_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.name = "user_1"
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        
        # 先创建缓存
        db.get_user_collection(user_id=1)
        assert 1 in db._user_collections
        
        # 删除集合
        success = db.delete_user_collection(user_id=1)
        
        assert success is True
        assert 1 not in db._user_collections
        mock_client_instance.delete_collection.assert_called_once_with(name="user_1")
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_list_user_collections(self, mock_embeddings, mock_chroma_client):
        """测试列出所有用户集合"""
        mock_client_instance = MagicMock()
        mock_collection1 = MagicMock()
        mock_collection1.name = "user_1"
        mock_collection2 = MagicMock()
        mock_collection2.name = "user_2"
        mock_client_instance.list_collections.return_value = [mock_collection1, mock_collection2]
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        collections = db.list_user_collections()
        
        assert len(collections) == 2
        assert "user_1" in collections
        assert "user_2" in collections


class TestSingletonPattern:
    """测试单例模式"""
    
    @patch("backend.app.database.vector_db.ChromaClient")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_get_vector_db_singleton(self, mock_embeddings, mock_chroma_client):
        """测试全局向量数据库实例单例"""
        mock_client_instance = MagicMock()
        mock_chroma_client.return_value = mock_client_instance
        mock_embeddings.return_value = MagicMock()
        
        # 清除全局实例（如果有）
        import backend.app.database.vector_db
        backend.app.database.vector_db._vector_db_instance = None
        
        db1 = get_vector_db()
        db2 = get_vector_db()
        
        assert db1 is db2
        mock_chroma_client.assert_called_once()
