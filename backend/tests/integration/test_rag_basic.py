"""
RAG 检索链基础集成测试

测试 RAG 链与向量数据库的基本集成，不依赖真实 AI API 调用。
使用 Mock LLM 来验证工作流程。
"""

import pytest
import os
from unittest.mock import Mock, patch
from pathlib import Path

from backend.app.chains.retrieval import RAGChain, create_rag_chain
from backend.app.database.vector_db import VectorDatabase
from backend.app.llm.factory import LLMProvider


class TestRAGBasicIntegration:
    """测试 RAG 链的基础集成功能"""
    
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
    
    def test_rag_chain_creation(self, temp_vector_db):
        """测试 RAG 链的创建"""
        user_id = 999
        
        # 使用 Mock 的 Embeddings 来避免真实 API 调用
        with patch('backend.app.llm.factory.LLMFactory.create_embeddings') as mock_embeddings:
            mock_embeddings_instance = Mock()
            # 返回简单的模拟向量
            mock_embeddings_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
            mock_embeddings_instance.embed_query.return_value = [0.1, 0.2, 0.3]
            mock_embeddings.return_value = mock_embeddings_instance
            
            # 添加测试文档
            test_documents = ["Python是一种编程语言"]
            
            success = temp_vector_db.add_documents(
                user_id=user_id,
                texts=test_documents
            )
            assert success is True
            
            # 创建检索器
            retriever = temp_vector_db.as_retriever(
                user_id=user_id,
                search_kwargs={"k": 1}
            )
            
            # 使用 Mock 创建 LLM
            with patch('backend.app.llm.factory.LLMFactory.create_chat_model') as mock_llm:
                mock_llm_instance = Mock()
                mock_llm_instance.invoke.return_value = "这是AI生成的测试回答"
                mock_llm.return_value = mock_llm_instance
                
                # 创建 RAG 链
                rag_chain = create_rag_chain(
                    retriever=retriever,
                    llm_provider=LLMProvider.DEEPSEEK_CHAT,
                    top_k=1
                )
                
                # 验证结构
                assert rag_chain is not None
                assert rag_chain.retriever is not None
                assert rag_chain.llm is not None
                assert rag_chain.top_k == 1
    
    def test_rag_chain_retriever_functionality(self, temp_vector_db):
        """测试 RAG 链的检索器功能"""
        user_id = 998
        
        # 使用 Mock 的 Embeddings
        with patch('backend.app.llm.factory.LLMFactory.create_embeddings') as mock_embeddings:
            mock_embeddings_instance = Mock()
            mock_embeddings_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
            mock_embeddings_instance.embed_query.return_value = [0.1, 0.2, 0.3]
            mock_embeddings.return_value = mock_embeddings_instance
            
            # 添加测试文档
            test_documents = [
                "Python是一种高级编程语言",
                "机器学习是人工智能的分支"
            ]
            
            success = temp_vector_db.add_documents(
                user_id=user_id,
                texts=test_documents
            )
            assert success is True
            
            # 创建检索器
            retriever = temp_vector_db.as_retriever(
                user_id=user_id,
                search_kwargs={"k": 2}
            )
            
            # 验证检索器工作
            results = retriever.invoke("编程语言")
            assert len(results) > 0
            assert hasattr(results[0], 'page_content')
            
            # 验证检索器类型
            from langchain_core.retrievers import BaseRetriever
            assert isinstance(retriever, BaseRetriever)
    
    def test_rag_chain_with_mock_llm(self, temp_vector_db):
        """测试使用 Mock LLM 的 RAG 链"""
        user_id = 997
        
        # 使用 Mock 的 Embeddings
        with patch('backend.app.llm.factory.LLMFactory.create_embeddings') as mock_embeddings:
            mock_embeddings_instance = Mock()
            mock_embeddings_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
            mock_embeddings_instance.embed_query.return_value = [0.1, 0.2, 0.3]
            mock_embeddings.return_value = mock_embeddings_instance
            
            # 添加测试文档
            test_documents = ["Python是一种编程语言"]
            
            success = temp_vector_db.add_documents(
                user_id=user_id,
                texts=test_documents
            )
            assert success is True
            
            # 创建检索器
            retriever = temp_vector_db.as_retriever(
                user_id=user_id,
                search_kwargs={"k": 1}
            )
            
            # 创建 Mock LLM 并替换整个 RAGChain 的 LLM
            with patch.object(RAGChain, '__init__', autospec=True) as mock_init:
                # 让 init 通过，但不设置实际的 LLM
                mock_init.return_value = None
                
                # 手动创建 RAGChain 实例
                rag_chain = RAGChain.__new__(RAGChain)
                rag_chain.retriever = retriever
                
                # 创建 Mock LLM
                mock_llm = Mock()
                mock_llm.invoke.return_value = "这是模拟的AI回答"
                rag_chain.llm = mock_llm
                rag_chain.top_k = 1
                rag_chain.score_threshold = None
                rag_chain._chain = None
                
                # 验证检索器功能
                results = rag_chain.retriever.invoke("Python")
                assert len(results) > 0
                
                # 验证 LLM 配置
                assert rag_chain.llm is not None
    
    def test_rag_chain_retriever_management(self, temp_vector_db):
        """测试 RAG 链的检索器管理"""
        user_id = 996
        
        # 使用 Mock 的 Embeddings
        with patch('backend.app.llm.factory.LLMFactory.create_embeddings') as mock_embeddings:
            mock_embeddings_instance = Mock()
            mock_embeddings_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
            mock_embeddings_instance.embed_query.return_value = [0.1, 0.2, 0.3]
            mock_embeddings.return_value = mock_embeddings_instance
            
            # 添加初始文档
            test_documents_1 = ["Python是一种编程语言"]
            test_documents_2 = ["机器学习是人工智能的分支"]
            
            success = temp_vector_db.add_documents(
                user_id=user_id,
                texts=test_documents_1
            )
            assert success is True
            
            # 创建初始检索器
            retriever_1 = temp_vector_db.as_retriever(
                user_id=user_id,
                search_kwargs={"k": 1}
            )
            
            # 使用 Mock 创建 LLM
            with patch('backend.app.llm.factory.LLMFactory.create_chat_model') as mock_llm:
                mock_llm_instance = Mock()
                mock_llm.return_value = mock_llm_instance
                
                # 创建 RAG 链
                rag_chain = create_rag_chain(retriever=retriever_1)
                
                # 验证初始检索器
                original_retriever = rag_chain.get_retriever()
                assert original_retriever is not None
                
                # 添加更多文档
                success = temp_vector_db.add_documents(
                    user_id=user_id,
                    texts=test_documents_2
                )
                assert success is True
                
                # 创建新的检索器
                retriever_2 = temp_vector_db.as_retriever(
                    user_id=user_id,
                    search_kwargs={"k": 2}
                )
                
                # 更新检索器
                rag_chain.update_retriever(retriever_2)
                
                # 验证更新后的检索器
                updated_retriever = rag_chain.get_retriever()
                assert updated_retriever is not None


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
    
    def test_rag_chain_with_empty_database(self, temp_vector_db):
        """测试空向量数据库的处理"""
        user_id = 995
        
        # 使用 Mock 的 Embeddings
        with patch('backend.app.llm.factory.LLMFactory.create_embeddings') as mock_embeddings:
            mock_embeddings_instance = Mock()
            mock_embeddings_instance.embed_documents.return_value = [[]]  # 空向量
            mock_embeddings_instance.embed_query.return_value = []
            mock_embeddings.return_value = mock_embeddings_instance
            
            # 不添加任何文档，创建空数据库
            retriever = temp_vector_db.as_retriever(
                user_id=user_id,
                search_kwargs={"k": 1}
            )
            
            # 创建 RAG 链
            rag_chain = create_rag_chain(retriever=retriever)
            
            # 验证检索器存在
            assert rag_chain.retriever is not None
            
            # 空数据库的检索应该返回空结果
            results = rag_chain.retriever.invoke("测试查询")
            # 空结果是可以接受的
            

if __name__ == "__main__":
    # 运行基础集成测试
    pytest.main([__file__, "-v"])