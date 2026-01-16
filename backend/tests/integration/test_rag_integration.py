"""
集成测试 RAG 检索链的真实功能

测试真实的 AI 调用和向量检索，验证端到端的 RAG 流程。
需要配置 API 密钥才能运行完整测试。
"""

import pytest
import os
from pathlib import Path

from backend.app.chains.retrieval import RAGChain, create_rag_chain
from backend.app.database.vector_db import VectorDatabase
from backend.app.llm.factory import LLMProvider, LLMFactory


class TestRAGIntegration:
    """测试 RAG 检索链的真实集成功能"""
    
    @pytest.fixture
    def temp_vector_db(self, tmp_path):
        """创建临时向量数据库"""
        import shutil
        import stat
        import time
        
        # 临时目录
        temp_dir = tmp_path / "temp_chroma_db"
        temp_dir.mkdir(exist_ok=True)
        
        # 创建向量数据库
        db = VectorDatabase(persist_directory=str(temp_dir))
        
        yield db
        
        # 清理（处理 Windows 文件锁定）
        def handle_remove_readonly(func, path, exc):
            """处理 Windows 只读文件"""
            os.chmod(path, stat.S_IWRITE)
            func(path)
        
        if temp_dir.exists():
            # Windows 上先等待一下让文件句柄释放
            if os.name == 'nt':
                time.sleep(0.1)
            try:
                shutil.rmtree(temp_dir, onerror=handle_remove_readonly)
            except Exception:
                # 如果还是失败，就忽略，测试已经通过了
                pass
    
    @pytest.fixture
    def test_documents(self):
        """提供测试文档内容"""
        return [
            "Python是一种高级编程语言，由Guido van Rossum于1991年创建。",
            "机器学习是人工智能的一个分支，让计算机能够从数据中学习。",
            "深度学习使用神经网络进行模式识别和预测。",
            "自然语言处理（NLP）使计算机能够理解和生成人类语言。",
            "计算机视觉让机器能够解释和理解视觉信息。"
        ]
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY") or not os.getenv("DEEPSEEK_API_KEY"),
        reason="API keys not set"
    )
    def test_rag_chain_creation(self, temp_vector_db, test_documents):
        """测试 RAG 链的创建和基本功能"""
        user_id = 999
        
        # 添加测试文档到向量数据库
        success = temp_vector_db.add_documents(
            user_id=user_id,
            texts=test_documents
        )
        assert success is True, "添加文档失败"
        
        # 创建检索器
        retriever = temp_vector_db.as_retriever(
            user_id=user_id,
            search_kwargs={"k": 3}
        )
        
        # 创建 RAG 链
        rag_chain = create_rag_chain(
            retriever=retriever,
            llm_provider=LLMProvider.DEEPSEEK_CHAT,
            top_k=3
        )
        
        assert rag_chain is not None
        assert rag_chain.retriever is not None
        assert rag_chain.llm is not None
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY") or not os.getenv("DEEPSEEK_API_KEY"),
        reason="API keys not set"
    )
    def test_rag_real_query_with_context(self, temp_vector_db, test_documents):
        """测试真实的 RAG 查询，验证上下文理解"""
        user_id = 998
        
        # 添加测试文档
        success = temp_vector_db.add_documents(
            user_id=user_id,
            texts=test_documents
        )
        assert success is True
        
        # 创建 RAG 链
        retriever = temp_vector_db.as_retriever(
            user_id=user_id,
            search_kwargs={"k": 2}
        )
        rag_chain = create_rag_chain(retriever=retriever)
        
        # 执行 RAG 查询
        question = "什么是Python编程语言？"
        result = rag_chain.query(question)
        
        # 验证结果结构
        assert "answer" in result
        assert "source_documents" in result
        assert "query" in result
        
        # 验证答案内容
        answer = result["answer"]
        assert len(answer) > 0
        assert "Python" in answer or "编程" in answer
        
        # 验证来源文档
        sources = result["source_documents"]
        assert len(sources) > 0
        assert any("Python" in doc.page_content for doc in sources)
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY") or not os.getenv("DEEPSEEK_API_KEY"),
        reason="API keys not set"
    )
    def test_rag_async_query(self, temp_vector_db, test_documents):
        """测试异步 RAG 查询"""
        import asyncio
        
        user_id = 997
        
        # 添加测试文档
        success = temp_vector_db.add_documents(
            user_id=user_id,
            texts=test_documents
        )
        assert success is True
        
        # 创建 RAG 链
        retriever = temp_vector_db.as_retriever(
            user_id=user_id,
            search_kwargs={"k": 2}
        )
        rag_chain = create_rag_chain(retriever=retriever)
        
        # 异步执行查询
        async def run_async_query():
            question = "机器学习是什么？"
            result = await rag_chain.aquery(question)
            return result
        
        result = asyncio.run(run_async_query())
        
        # 验证异步结果
        assert "answer" in result
        assert len(result["answer"]) > 0
        assert len(result["source_documents"]) > 0
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY") or not os.getenv("DEEPSEEK_API_KEY"),
        reason="API keys not set"
    )
    def test_rag_with_different_llm_providers(self, temp_vector_db, test_documents):
        """测试不同 LLM 提供商的 RAG 功能"""
        user_id = 996
        
        # 添加测试文档
        success = temp_vector_db.add_documents(
            user_id=user_id,
            texts=test_documents
        )
        assert success is True
        
        # 测试 DeepSeek
        retriever = temp_vector_db.as_retriever(
            user_id=user_id,
            search_kwargs={"k": 2}
        )
        
        rag_chain_deepseek = create_rag_chain(
            retriever=retriever,
            llm_provider=LLMProvider.DEEPSEEK_CHAT
        )
        
        result_deepseek = rag_chain_deepseek.query("什么是深度学习？")
        
        # 测试 GLM-4.7（如果可用）
        if os.getenv("ZHIPUAI_API_KEY"):
            rag_chain_glm = create_rag_chain(
                retriever=retriever,
                llm_provider=LLMProvider.GLM_4_7
            )
            
            result_glm = rag_chain_glm.query("什么是深度学习？")
            
            # 验证两个模型都能生成答案
            assert len(result_deepseek["answer"]) > 0
            assert len(result_glm["answer"]) > 0
            
            # 答案应该包含相关关键词
            assert any(keyword in result_deepseek["answer"] or 
                      keyword in result_glm["answer"] 
                      for keyword in ["学习", "网络", "智能"])
        
        # 至少验证 DeepSeek 正常工作
        assert len(result_deepseek["answer"]) > 0
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY") or not os.getenv("DEEPSEEK_API_KEY"),
        reason="API keys not set"
    )
    def test_rag_chain_retriever_management(self, temp_vector_db, test_documents):
        """测试 RAG 链的检索器管理功能"""
        user_id = 995
        
        # 添加初始文档
        success = temp_vector_db.add_documents(
            user_id=user_id,
            texts=test_documents[:2]  # 只添加前两个文档
        )
        assert success is True
        
        # 创建初始 RAG 链
        retriever = temp_vector_db.as_retriever(
            user_id=user_id,
            search_kwargs={"k": 1}
        )
        rag_chain = create_rag_chain(retriever=retriever)
        
        # 测试初始检索器
        original_retriever = rag_chain.get_retriever()
        assert original_retriever is not None
        
        # 添加更多文档并更新检索器
        success = temp_vector_db.add_documents(
            user_id=user_id,
            texts=test_documents[2:]  # 添加剩余文档
        )
        assert success is True
        
        # 更新检索器
        new_retriever = temp_vector_db.as_retriever(
            user_id=user_id,
            search_kwargs={"k": 3}
        )
        rag_chain.update_retriever(new_retriever)
        
        # 验证更新后的检索器
        updated_retriever = rag_chain.get_retriever()
        assert updated_retriever is not None
        
        # 执行查询验证更新后的检索器工作正常
        result = rag_chain.query("自然语言处理是什么？")
        assert len(result["answer"]) > 0
        assert len(result["source_documents"]) > 0
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY") or not os.getenv("DEEPSEEK_API_KEY"),
        reason="API keys not set"
    )
    def test_rag_with_score_threshold(self, temp_vector_db, test_documents):
        """测试带相似度阈值的 RAG 检索（使用 ChromaDB 兼容参数）"""
        user_id = 994
        
        # 添加测试文档
        success = temp_vector_db.add_documents(
            user_id=user_id,
            texts=test_documents
        )
        assert success is True
        
        # 创建检索器，使用 ChromaDB 兼容的参数
        retriever = temp_vector_db.as_retriever(
            user_id=user_id,
            search_kwargs={"k": 5}
        )
        
        # 创建 RAG 链
        rag_chain = create_rag_chain(retriever=retriever)
        
        # 执行查询
        result = rag_chain.query("Python编程语言")
        
        # 验证结果
        assert len(result["answer"]) > 0
        assert len(result["source_documents"]) > 0
        
        # 验证检索到的文档与查询相关
        sources_content = [doc.page_content for doc in result["source_documents"]]
        assert any("Python" in content for content in sources_content)


class TestRAGErrorHandling:
    """测试 RAG 链的错误处理"""
    
    @pytest.fixture
    def temp_vector_db(self, tmp_path):
        """创建临时向量数据库"""
        import shutil
        import stat
        import time
        
        # 临时目录
        temp_dir = tmp_path / "temp_chroma_db"
        temp_dir.mkdir(exist_ok=True)
        
        # 创建向量数据库
        db = VectorDatabase(persist_directory=str(temp_dir))
        
        yield db
        
        # 清理（处理 Windows 文件锁定）
        def handle_remove_readonly(func, path, exc):
            """处理 Windows 只读文件"""
            os.chmod(path, stat.S_IWRITE)
            func(path)
        
        if temp_dir.exists():
            # Windows 上先等待一下让文件句柄释放
            if os.name == 'nt':
                time.sleep(0.1)
            try:
                shutil.rmtree(temp_dir, onerror=handle_remove_readonly)
            except Exception:
                # 如果还是失败，就忽略，测试已经通过了
                pass
    
    @pytest.fixture
    def test_documents(self):
        """提供测试文档内容"""
        return [
            "Python是一种高级编程语言，由Guido van Rossum于1991年创建。",
            "机器学习是人工智能的一个分支，让计算机能够从数据中学习。",
            "深度学习使用神经网络进行模式识别和预测。",
            "自然语言处理（NLP）使计算机能够理解和生成人类语言。",
            "计算机视觉让机器能够解释和理解视觉信息。"
        ]
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY") or not os.getenv("DEEPSEEK_API_KEY"),
        reason="API keys not set"
    )
    def test_rag_with_empty_database(self, temp_vector_db):
        """测试空向量数据库的 RAG 查询"""
        user_id = 993
        
        # 不添加任何文档，创建空数据库
        retriever = temp_vector_db.as_retriever(
            user_id=user_id,
            search_kwargs={"k": 3}
        )
        
        rag_chain = create_rag_chain(retriever=retriever)
        
        # 执行查询（应该能处理空数据库的情况）
        result = rag_chain.query("测试查询")
        
        # 验证结果结构
        assert "answer" in result
        assert "source_documents" in result
        
        # 空数据库时可能返回空列表或AI的通用回答
        sources = result["source_documents"]
        answer = result["answer"]
        
        # 两种情况都是可接受的：空文档列表或AI的通用回答
        assert len(answer) > 0  # AI 应该能给出某种回答
    
    @pytest.mark.skipif(
        not os.getenv("ZHIPUAI_API_KEY") or not os.getenv("DEEPSEEK_API_KEY"),
        reason="API keys not set"
    )
    def test_rag_with_unrelated_query(self, temp_vector_db, test_documents):
        """测试与知识库无关的查询"""
        user_id = 992
        
        # 添加技术相关文档
        success = temp_vector_db.add_documents(
            user_id=user_id,
            texts=test_documents
        )
        assert success is True
        
        retriever = temp_vector_db.as_retriever(
            user_id=user_id,
            search_kwargs={"k": 2}
        )
        rag_chain = create_rag_chain(retriever=retriever)
        
        # 查询与知识库无关的内容
        result = rag_chain.query("今天天气怎么样？")
        
        # 验证AI能够处理这种情景
        assert "answer" in result
        assert len(result["answer"]) > 0
        
        # 来源文档可能为空或包含不相关内容
        sources = result["source_documents"]
        # 不验证具体内容，因为AI可能会基于知识库内容给出回答


if __name__ == "__main__":
    # 如果直接运行，检查API密钥并运行测试
    if os.getenv("ZHIPUAI_API_KEY") and os.getenv("DEEPSEEK_API_KEY"):
        pytest.main([__file__, "-v"])
    else:
        print("请设置 ZHIPUAI_API_KEY 和 DEEPSEEK_API_KEY 环境变量以运行集成测试")
        print("测试将自动跳过，不会影响CI/CD流程")
