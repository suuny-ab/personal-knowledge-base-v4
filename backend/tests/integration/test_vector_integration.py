"""
Integration tests for Vector Database

Tests real embedding generation and vector storage without mocks.
Requires API keys to be configured.
"""

import pytest
import os
from pathlib import Path

from backend.app.database.vector_db import VectorDatabase
from backend.app.llm.factory import LLMFactory, EmbeddingProvider


class TestEmbeddingGeneration:
    """测试真实的 Embedding 生成"""
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY"),
        reason="ZHIPUAI_API_KEY not set"
    )
    def test_create_embeddings_real(self):
        """测试真实的 Embedding 生成"""
        embeddings = LLMFactory.create_embeddings(
            provider=EmbeddingProvider.ZHIPUAI_EMBEDDING_3
        )
        
        # 测试 embedding 生成
        test_texts = ["这是一个测试句子", "这是另一个测试句子"]
        
        # 调用真实的 embedding 方法
        result = embeddings.embed_documents(test_texts)
        
        assert result is not None
        assert len(result) == 2
        assert len(result[0]) > 0  # embedding 向量应该有维度
        assert len(result[1]) > 0
        assert len(result[0]) == len(result[1])  # 两个向量维度应该相同
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY"),
        reason="ZHIPUAI_API_KEY not set"
    )
    def test_create_embeddings_single(self):
        """测试单个文本的 Embedding 生成"""
        embeddings = LLMFactory.create_embeddings()
        
        result = embeddings.embed_query("测试查询")
        
        assert result is not None
        assert len(result) > 0
        print(f"Embedding dimension: {len(result)}")
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY"),
        reason="ZHIPUAI_API_KEY not set"
    )
    def test_llm_factory_embeddings(self):
        """测试 LLM Factory 创建的 Embeddings 是正确的类型"""
        embeddings = LLMFactory.create_embeddings()
        
        # 验证类型
        from langchain_community.embeddings import ZhipuAIEmbeddings
        assert isinstance(embeddings, ZhipuAIEmbeddings)
        
        # 验证配置
        assert embeddings.model == "embedding-3"


class TestRealVectorStorage:
    """测试真实的向量存储和检索"""
    
    @pytest.fixture
    def temp_vector_db(self, tmp_path):
        """创建临时向量数据库"""
        import shutil
        
        # 临时目录
        temp_dir = tmp_path / "temp_chroma_db"
        temp_dir.mkdir(exist_ok=True)
        
        # 创建向量数据库
        db = VectorDatabase(persist_directory=str(temp_dir))
        
        yield db
        
        # 清理
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY"),
        reason="ZHIPUAI_API_KEY not set"
    )
    def test_add_and_search_real_documents(self, temp_vector_db):
        """测试真实的文档添加和检索"""
        user_id = 999  # 使用测试用户ID
        
        # 添加测试文档
        documents = [
            "Python是一种高级编程语言",
            "JavaScript主要用于网页开发",
            "机器学习是人工智能的一个分支"
        ]
        
        success = temp_vector_db.add_documents(
            user_id=user_id,
            texts=documents
        )
        
        assert success is True, "添加文档失败"
        
        # 检索相关文档
        results = temp_vector_db.search(
            user_id=user_id,
            query="编程语言",
            n_results=2
        )
        
        assert "documents" in results
        assert len(results["documents"][0]) > 0
        
        # 验证检索结果的相关性
        retrieved_docs = results["documents"][0]
        assert any("编程" in doc for doc in retrieved_docs), \
            "检索结果应该包含'编程'"
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY"),
        reason="ZHIPUAI_API_KEY not set"
    )
    def test_semantic_search_accuracy(self, temp_vector_db):
        """测试语义检索的准确性"""
        user_id = 998
        
        # 添加相关和不相关的文档
        documents = [
            "深度学习是机器学习的一个子领域",
            "今天天气很好，适合出去游玩",
            "神经网络是深度学习的基础"
        ]
        
        success = temp_vector_db.add_documents(
            user_id=user_id,
            texts=documents
        )
        assert success is True
        
        # 查询"人工智能"相关内容
        results = temp_vector_db.search(
            user_id=user_id,
            query="人工智能技术",
            n_results=2
        )
        
        retrieved_docs = results["documents"][0]
        
        # 验证检索的是相关文档，而不是天气文档
        assert any("学习" in doc for doc in retrieved_docs), \
            "应该检索到'学习'相关文档"
        assert not any("天气" in doc for doc in retrieved_docs), \
            "不应该检索到'天气'文档"
        
        # 验证相似度分数
        distances = results["distances"][0]
        assert len(distances) > 0
        assert all(d >= 0 and d <= 1 for d in distances), \
            "距离应该在 [0, 1] 范围内"
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY"),
        reason="ZHIPUAI_API_KEY not set"
    )
    def test_retriever_conversion(self, temp_vector_db):
        """测试 Retriever 转换功能"""
        user_id = 997
        
        # 添加文档
        success = temp_vector_db.add_documents(
            user_id=user_id,
            texts=["测试文档内容"]
        )
        assert success is True
        
        # 转换为 retriever
        retriever = temp_vector_db.as_retriever(
            user_id=user_id,
            search_kwargs={"k": 3}
        )
        
        assert retriever is not None
        
        # 验证 retriever 类型
        from langchain_core.retrievers import BaseRetriever
        assert isinstance(retriever, BaseRetriever)
        
        # 测试 retriever 检索
        results = retriever.invoke("测试查询")
        
        assert len(results) > 0
        assert results[0].page_content is not None
