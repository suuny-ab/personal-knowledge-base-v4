"""
Unit tests for RAG Chain
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from langchain_core.documents import Document

from backend.app.chains.retrieval import RAGChain, create_rag_chain
from backend.app.llm.factory import LLMProvider


class TestRAGChain:
    """测试 RAGChain 类"""
    
    @pytest.fixture
    def mock_retriever(self):
        """创建模拟检索器"""
        retriever = Mock()
        retriever.invoke.return_value = [
            Document(page_content="Python是一种高级编程语言", metadata={"source": "test1"}),
            Document(page_content="JavaScript主要用于网页开发", metadata={"source": "test2"})
        ]
        return retriever
    
    @pytest.fixture
    def mock_llm(self):
        """创建模拟 LLM"""
        llm = Mock()
        llm.invoke.return_value = "根据背景信息，Python是一种高级编程语言，而JavaScript主要用于网页开发。"
        return llm
    
    def test_rag_chain_initialization(self, mock_retriever, mock_llm):
        """测试 RAGChain 初始化"""
        chain = RAGChain(
            retriever=mock_retriever,
            llm=mock_llm,
            top_k=5
        )
        
        assert chain.retriever == mock_retriever
        assert chain.llm == mock_llm
        assert chain.top_k == 5
        assert chain._chain is None  # 延迟构建，初始化时为 None
    
    def test_query_method(self, mock_retriever, mock_llm):
        """测试 query 方法"""
        # 设置 mock 返回值
        mock_retriever.invoke.return_value = [
            Document(page_content="Python是一种高级编程语言", metadata={"source": "test1"}),
            Document(page_content="JavaScript主要用于网页开发", metadata={"source": "test2"})
        ]
        
        chain = RAGChain(
            retriever=mock_retriever,
            llm=mock_llm
        )
        
        # 手动设置 mock 链的返回值
        chain._chain = Mock()
        chain._chain.invoke.return_value = "根据背景信息，Python是一种高级编程语言。"
        
        result = chain.query("什么是Python？")
        
        # 验证返回结果
        assert "answer" in result
        assert "source_documents" in result
        assert "query" in result
        assert result["query"] == "什么是Python？"
        assert result["answer"] == "根据背景信息，Python是一种高级编程语言。"
        assert len(result["source_documents"]) == 2
        
        # 验证检索器被调用
        mock_retriever.invoke.assert_called_once_with("什么是Python？")
    
    @pytest.mark.asyncio
    async def test_aquery_method(self, mock_retriever):
        """测试异步 aquery 方法"""
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(return_value="这是AI的回答")
        
        # 设置 mock 检索器的异步方法
        async def mock_ainvoke(query):
            return [
                Document(page_content="Python是一种高级编程语言", metadata={"source": "test1"})
            ]
        mock_retriever.ainvoke = AsyncMock(side_effect=mock_ainvoke)
        
        chain = RAGChain(
            retriever=mock_retriever,
            llm=mock_llm
        )
        
        # 手动设置 mock 链的异步方法
        async def mock_chain_invoke(query):
            return "这是AI的回答"
        chain._chain = Mock()
        chain._chain.ainvoke = AsyncMock(side_effect=mock_chain_invoke)
        
        result = await chain.aquery("什么是Python？")
        
        assert "answer" in result
        assert result["query"] == "什么是Python？"
        assert result["answer"] == "这是AI的回答"
        assert len(result["source_documents"]) == 1
    
    def test_get_retriever(self, mock_retriever, mock_llm):
        """测试获取检索器"""
        chain = RAGChain(
            retriever=mock_retriever,
            llm=mock_llm
        )
        
        retrieved = chain.get_retriever()
        assert retrieved == mock_retriever
    
    def test_update_retriever(self, mock_retriever, mock_llm):
        """测试更新检索器"""
        chain = RAGChain(
            retriever=mock_retriever,
            llm=mock_llm
        )
        
        # 创建新的检索器
        new_retriever = Mock()
        chain.update_retriever(new_retriever)
        
        assert chain.retriever == new_retriever
        assert chain._chain is None  # 更新检索器后重置了链
    
    def test_score_threshold_none(self, mock_retriever, mock_llm):
        """测试不设置相似度阈值"""
        chain = RAGChain(
            retriever=mock_retriever,
            llm=mock_llm,
            score_threshold=None
        )
        
        assert chain.score_threshold is None
    
    def test_score_threshold_set(self, mock_retriever, mock_llm):
        """测试设置相似度阈值"""
        chain = RAGChain(
            retriever=mock_retriever,
            llm=mock_llm,
            score_threshold=0.7
        )
        
        assert chain.score_threshold == 0.7


class TestCreateRAGChain:
    """测试 create_rag_chain 工厂函数"""
    
    @pytest.fixture
    def mock_retriever(self):
        """创建模拟检索器"""
        return Mock()
    
    def test_create_rag_chain_with_default_params(self, mock_retriever):
        """测试使用默认参数创建 RAG 链"""
        chain = create_rag_chain(mock_retriever)
        
        assert isinstance(chain, RAGChain)
        assert chain.top_k == 5
        assert chain.score_threshold is None
    
    def test_create_rag_chain_with_custom_params(self, mock_retriever):
        """测试使用自定义参数创建 RAG 链"""
        chain = create_rag_chain(
            retriever=mock_retriever,
            llm_provider=LLMProvider.GLM_4_7,
            top_k=10,
            score_threshold=0.8
        )
        
        assert isinstance(chain, RAGChain)
        assert chain.top_k == 10
        assert chain.score_threshold == 0.8
    
    def test_create_rag_chain_retriever_set(self, mock_retriever):
        """测试检索器正确设置"""
        chain = create_rag_chain(mock_retriever)
        
        assert chain.retriever == mock_retriever


class TestPromptTemplate:
    """测试提示词模板"""
    
    @pytest.fixture
    def mock_retriever(self):
        """创建模拟检索器"""
        return Mock()
    
    def test_prompt_template_exists(self, mock_retriever):
        """测试提示词模板存在"""
        chain = RAGChain(retriever=mock_retriever)
        
        assert chain.prompt is not None
    
    def test_prompt_template_messages(self, mock_retriever):
        """测试提示词模板包含系统消息和用户消息"""
        chain = RAGChain(retriever=mock_retriever)
        
        messages = chain.prompt.messages
        assert len(messages) == 2  # system 和 user 消息
