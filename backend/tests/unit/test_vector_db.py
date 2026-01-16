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
    
    @patch("backend.app.database.vector_db.Chroma")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_init_vector_db(self, mock_embeddings, mock_chroma_class):
        """测试向量数据库初始化"""
        mock_chroma_instance = MagicMock()
        mock_chroma_class.return_value = mock_chroma_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        
        assert db.embeddings is not None
        assert db.persist_directory.exists()
        mock_embeddings.assert_called_once_with(provider=EmbeddingProvider.ZHIPUAI_EMBEDDING_3)
    
    @patch("backend.app.database.vector_db.Chroma")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_init_with_custom_directory(self, mock_embeddings, mock_chroma_class):
        """测试使用自定义目录初始化"""
        mock_chroma_instance = MagicMock()
        mock_chroma_class.return_value = mock_chroma_instance
        mock_embeddings.return_value = MagicMock()
        
        custom_dir = "/tmp/test_chroma_db"
        db = VectorDatabase(persist_directory=custom_dir)
        
        # 比较路径对象而非字符串，避免不同操作系统的路径分隔符差异
        assert db.persist_directory == Path(custom_dir)
    
    @patch("backend.app.database.vector_db.Chroma")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_get_user_vectorstore_new(self, mock_embeddings, mock_chroma_class):
        """测试获取新用户向量存储"""
        mock_chroma_instance = MagicMock()
        mock_chroma_instance._collection.count.return_value = 0
        mock_chroma_class.return_value = mock_chroma_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        vectorstore = db.get_user_vectorstore(user_id=1)
        
        assert vectorstore is not None
        mock_chroma_class.assert_called_once()
    
    @patch("backend.app.database.vector_db.Chroma")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_get_user_vectorstore_cached(self, mock_embeddings, mock_chroma_class):
        """测试获取缓存的用户向量存储"""
        mock_chroma_instance = MagicMock()
        mock_chroma_instance._collection.count.return_value = 0
        mock_chroma_class.return_value = mock_chroma_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        
        # 第一次获取
        vectorstore1 = db.get_user_vectorstore(user_id=1)
        # 第二次获取（应该从缓存中获取）
        vectorstore2 = db.get_user_vectorstore(user_id=1)
        
        assert vectorstore1 is vectorstore2
        mock_chroma_class.assert_called_once()


class TestVectorOperations:
    """测试向量操作"""
    
    @patch("backend.app.database.vector_db.Chroma")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_add_documents(self, mock_embeddings, mock_chroma_class):
        """测试添加文档"""
        mock_chroma_instance = MagicMock()
        mock_chroma_instance.add_texts.return_value = None
        mock_chroma_class.return_value = mock_chroma_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        success = db.add_documents(
            user_id=1,
            texts=["文档1", "文档2"],
            metadatas=[{"source": "test1"}, {"source": "test2"}]
        )
        
        assert success is True
        mock_chroma_instance.add_texts.assert_called_once()
    
    @patch("backend.app.database.vector_db.Chroma")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_search_documents(self, mock_embeddings, mock_chroma_class):
        """测试检索文档"""
        mock_chroma_instance = MagicMock()
        mock_doc1 = MagicMock()
        mock_doc1.page_content = "结果1"
        mock_doc1.metadata = {"source": "test"}
        mock_doc2 = MagicMock()
        mock_doc2.page_content = "结果2"
        mock_doc2.metadata = {"source": "test"}
        mock_chroma_instance.similarity_search_with_relevance_scores.return_value = [
            (mock_doc1, 0.9),
            (mock_doc2, 0.8)
        ]
        mock_chroma_class.return_value = mock_chroma_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        results = db.search(user_id=1, query="测试查询", n_results=5)
        
        assert "documents" in results
        assert len(results["documents"]) == 1
        mock_chroma_instance.similarity_search_with_relevance_scores.assert_called_once()
    
    @patch("backend.app.database.vector_db.Chroma")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_delete_documents(self, mock_embeddings, mock_chroma_class):
        """测试删除文档"""
        mock_chroma_instance = MagicMock()
        mock_chroma_instance.delete.return_value = None
        mock_chroma_class.return_value = mock_chroma_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        success = db.delete_documents(user_id=1, ids=["doc1", "doc2"])
        
        assert success is True
        mock_chroma_instance.delete.assert_called_once_with(ids=["doc1", "doc2"])
    
    @patch("backend.app.database.vector_db.Chroma")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_get_collection_stats(self, mock_embeddings, mock_chroma_class):
        """测试获取集合统计信息"""
        mock_chroma_instance = MagicMock()
        mock_chroma_instance._collection.count.return_value = 10
        mock_chroma_class.return_value = mock_chroma_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        stats = db.get_collection_stats(user_id=1)
        
        assert stats["user_id"] == 1
        assert stats["count"] == 10


class TestCollectionManagement:
    """测试集合管理"""
    
    @patch("backend.app.database.vector_db.Chroma")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_delete_user_collection(self, mock_embeddings, mock_chroma_class):
        """测试删除用户集合"""
        mock_chroma_instance = MagicMock()
        mock_chroma_instance.delete_collection.return_value = None
        mock_chroma_class.return_value = mock_chroma_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        
        # 先创建缓存
        db.get_user_vectorstore(user_id=1)
        assert 1 in db._user_vectorstores
        
        # 删除集合
        success = db.delete_user_collection(user_id=1)
        
        assert success is True
        assert 1 not in db._user_vectorstores
        mock_chroma_instance.delete_collection.assert_called_once()


class TestSingletonPattern:
    """测试单例模式"""
    
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_get_vector_db_singleton(self, mock_embeddings):
        """测试全局向量数据库实例单例"""
        mock_embeddings.return_value = MagicMock()
        
        # 清除全局实例（如果有）
        import backend.app.database.vector_db
        backend.app.database.vector_db._vector_db_instance = None
        
        db1 = get_vector_db()
        db2 = get_vector_db()
        
        assert db1 is db2
        mock_embeddings.assert_called_once()


class TestRetriever:
    """测试 Retriever 转换"""
    
    @patch("backend.app.database.vector_db.Chroma")
    @patch("backend.app.database.vector_db.LLMFactory.create_embeddings")
    def test_as_retriever(self, mock_embeddings, mock_chroma_class):
        """测试转换为 Retriever"""
        mock_chroma_instance = MagicMock()
        mock_retriever = MagicMock()
        mock_chroma_instance.as_retriever.return_value = mock_retriever
        mock_chroma_class.return_value = mock_chroma_instance
        mock_embeddings.return_value = MagicMock()
        
        db = VectorDatabase()
        retriever = db.as_retriever(user_id=1, search_kwargs={"k": 10})
        
        assert retriever is not None
        mock_chroma_instance.as_retriever.assert_called_once_with(
            search_type="similarity",
            search_kwargs={"k": 10}
        )
