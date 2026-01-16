"""
Unit tests for Vector Service

Tests vector storage service integration.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from backend.app.services.vector_service import VectorService, get_vector_service
from backend.app.utils.chunker import ChunkingStrategy


class TestVectorServiceInit:
    """测试向量服务初始化"""
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_init_with_default_db(self, mock_get_db):
        """测试使用默认数据库初始化"""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        
        assert service.vector_db == mock_db
        mock_get_db.assert_called_once()
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_init_with_custom_db(self, mock_get_db):
        """测试使用自定义数据库初始化"""
        custom_db = MagicMock()
        service = VectorService(vector_db=custom_db)
        
        assert service.vector_db == custom_db
        mock_get_db.assert_not_called()


class TestIndexDocument:
    """测试文档索引"""
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_index_document_success(self, mock_get_db):
        """测试成功索引文档"""
        mock_db = MagicMock()
        mock_db.add_documents.return_value = True
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.index_document(
            user_id=1,
            text="这是一个测试文档。" * 20,
            metadata={"doc_id": "test1", "source": "test.txt"}
        )
        
        assert result["success"] is True
        assert result["indexed_chunks"] > 0
        assert "成功索引" in result["message"]
        mock_db.add_documents.assert_called_once()
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_index_markdown_document(self, mock_get_db):
        """测试索引Markdown文档"""
        mock_db = MagicMock()
        mock_db.add_documents.return_value = True
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.index_document(
            user_id=1,
            text="# 标题\n内容",
            metadata={"doc_id": "test_md"},
            is_markdown=True
        )
        
        assert result["success"] is True
        assert result["indexed_chunks"] > 0
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_index_empty_document(self, mock_get_db):
        """测试索引空文档"""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.index_document(
            user_id=1,
            text="",
            metadata={"doc_id": "empty"}
        )
        
        assert result["success"] is False
        assert result["indexed_chunks"] == 0
        assert "文档为空" in result["message"]
        mock_db.add_documents.assert_not_called()
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_index_document_with_strategy(self, mock_get_db):
        """测试使用指定策略索引文档"""
        mock_db = MagicMock()
        mock_db.add_documents.return_value = True
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.index_document(
            user_id=1,
            text="这是第一句。这是第二句。" * 20,
            metadata={"doc_id": "test"},
            chunking_strategy=ChunkingStrategy.FIXED_SIZE
        )
        
        assert result["success"] is True


class TestIndexFile:
    """测试文件索引"""
    
    @patch("backend.app.services.vector_service.get_vector_db")
    @patch("pathlib.Path.exists")
    @patch("builtins.open", create=True)
    def test_index_file_success(self, mock_open_func, mock_exists, mock_get_db):
        """测试成功索引文件"""
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.read.return_value = "这是文件内容。" * 20
        mock_open_func.return_value.__enter__.return_value = mock_file
        
        mock_db = MagicMock()
        mock_db.add_documents.return_value = True
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.index_file(
            user_id=1,
            file_path="/test/file.txt",
            metadata={"doc_id": "file1"}
        )
        
        assert result["success"] is True
        assert result["indexed_chunks"] > 0
        mock_db.add_documents.assert_called_once()
    
    @patch("backend.app.services.vector_service.get_vector_db")
    @patch("pathlib.Path.exists")
    def test_index_file_not_exists(self, mock_exists, mock_get_db):
        """测试索引不存在的文件"""
        mock_exists.return_value = False
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.index_file(
            user_id=1,
            file_path="/nonexistent/file.txt"
        )
        
        assert result["success"] is False
        assert "文件不存在" in result["message"]
        mock_db.add_documents.assert_not_called()
    
    @patch("backend.app.services.vector_service.get_vector_db")
    @patch("pathlib.Path.exists")
    @patch("builtins.open", create=True)
    def test_index_markdown_file(self, mock_open_func, mock_exists, mock_get_db):
        """测试索引Markdown文件"""
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.read.return_value = "# 标题\n内容"
        mock_open_func.return_value.__enter__.return_value = mock_file
        
        mock_db = MagicMock()
        mock_db.add_documents.return_value = True
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.index_file(
            user_id=1,
            file_path="/test/file.md"
        )
        
        assert result["success"] is True


class TestSearch:
    """测试向量检索"""
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_search_success(self, mock_get_db):
        """测试成功检索"""
        mock_db = MagicMock()
        mock_db.search.return_value = {
            "documents": [["结果1", "结果2"]],
            "metadatas": [[{"source": "test1"}, {"source": "test2"}]],
            "distances": [[0.1, 0.2]],
            "ids": [["doc1", "doc2"]]
        }
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.search(
            user_id=1,
            query="测试查询",
            n_results=5
        )
        
        assert result["success"] is True
        assert result["query"] == "测试查询"
        assert len(result["results"]) == 2
        assert result["total_results"] == 2
        
        # 检查第一个结果
        first_result = result["results"][0]
        assert first_result["content"] == "结果1"
        assert first_result["metadata"]["source"] == "test1"
        assert first_result["distance"] == 0.1
        assert abs(first_result["similarity"] - 0.9) < 0.01
        
        mock_db.search.assert_called_once()
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_search_with_filter(self, mock_get_db):
        """测试使用元数据过滤检索"""
        mock_db = MagicMock()
        mock_db.search.return_value = {
            "documents": [["结果"]],
            "metadatas": [[{"source": "filtered"}]],
            "distances": [[0.1]],
            "ids": [["doc1"]]
        }
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.search(
            user_id=1,
            query="测试",
            filter_metadata={"source": "filtered"}
        )
        
        assert result["success"] is True
        mock_db.search.assert_called_once_with(
            user_id=1,
            query="测试",
            n_results=5,
            filter_metadata={"source": "filtered"}
        )
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_search_empty_results(self, mock_get_db):
        """测试检索空结果"""
        mock_db = MagicMock()
        mock_db.search.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
            "ids": [[]]
        }
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.search(
            user_id=1,
            query="不存在的查询"
        )
        
        assert result["success"] is True
        assert result["total_results"] == 0
        assert len(result["results"]) == 0


class TestDeleteDocument:
    """测试文档删除"""
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_delete_document_success(self, mock_get_db):
        """测试成功删除文档"""
        mock_db = MagicMock()
        mock_db.search.return_value = {
            "ids": [["doc1_chunk_0", "doc1_chunk_1", "doc2_chunk_0"]]
        }
        mock_db.delete_documents.return_value = True
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.delete_document(
            user_id=1,
            doc_id="doc1"
        )
        
        assert result["success"] is True
        assert result["deleted_chunks"] == 2  # doc1 有2个分块
        assert "成功删除 2 个文档块" in result["message"]
        mock_db.delete_documents.assert_called_once_with(
            user_id=1,
            ids=["doc1_chunk_0", "doc1_chunk_1"]
        )
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_delete_document_not_found(self, mock_get_db):
        """测试删除不存在的文档"""
        mock_db = MagicMock()
        mock_db.search.return_value = {
            "ids": [["doc2_chunk_0"]]
        }
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.delete_document(
            user_id=1,
            doc_id="doc1"
        )
        
        assert result["success"] is False
        assert result["deleted_chunks"] == 0
        assert "未找到文档" in result["message"]
        mock_db.delete_documents.assert_not_called()


class TestCollectionManagement:
    """测试集合管理"""
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_get_collection_stats(self, mock_get_db):
        """测试获取集合统计信息"""
        mock_db = MagicMock()
        mock_db.get_collection_stats.return_value = {"user_id": 1, "count": 100}
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.get_collection_stats(user_id=1)
        
        assert result["success"] is True
        assert result["user_id"] == 1
        assert result["total_chunks"] == 100
        mock_db.get_collection_stats.assert_called_once_with(1)
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_clear_collection(self, mock_get_db):
        """测试清空集合"""
        mock_db = MagicMock()
        mock_db.delete_user_collection.return_value = True
        mock_get_db.return_value = mock_db
        
        service = VectorService()
        result = service.clear_collection(user_id=1)
        
        assert result["success"] is True
        assert "清空成功" in result["message"]
        mock_db.delete_user_collection.assert_called_once_with(1)


class TestSingletonPattern:
    """测试单例模式"""
    
    @patch("backend.app.services.vector_service.get_vector_db")
    def test_get_vector_service_singleton(self, mock_get_db):
        """测试全局向量服务实例单例"""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # 清除全局实例（如果有）
        import backend.app.services.vector_service
        backend.app.services.vector_service._vector_service_instance = None
        
        service1 = get_vector_service()
        service2 = get_vector_service()
        
        assert service1 is service2
        mock_get_db.assert_called_once()
