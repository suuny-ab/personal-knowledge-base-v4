"""
ChromaDB 向量数据库配置

使用 LangChain 官方 Chroma 类实现，提供用户隔离的向量存储系统。
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import ZhipuAIEmbeddings

from backend.app.llm.factory import EmbeddingProvider, LLMFactory


class VectorDatabase:
    """向量数据库管理类，提供用户隔离的向量存储"""
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        embedding_provider: EmbeddingProvider = EmbeddingProvider.ZHIPUAI_EMBEDDING_3
    ):
        """
        初始化向量数据库
        
        Args:
            persist_directory: 向量数据库持久化目录
            embedding_provider: Embedding提供商
        """
        if persist_directory is None:
            # 默认存储在 data/chroma_db
            persist_directory = str(Path(__file__).parent.parent.parent.parent / "data" / "chroma_db")
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # 使用 LangChain 的 ZhipuAIEmbeddings
        self.embeddings = LLMFactory.create_embeddings(provider=embedding_provider)
        
        # 缓存用户向量存储
        self._user_vectorstores: Dict[int, Chroma] = {}
    
    def get_user_vectorstore(self, user_id: int) -> Chroma:
        """
        获取或创建用户的向量存储
        
        Args:
            user_id: 用户ID
            
        Returns:
            LangChain Chroma VectorStore 对象
        """
        if user_id in self._user_vectorstores:
            return self._user_vectorstores[user_id]
        
        collection_name = f"user_{user_id}"
        
        # 创建或加载用户的 Chroma 向量存储
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory)
        )
        
        self._user_vectorstores[user_id] = vectorstore
        return vectorstore
    
    def add_documents(
        self,
        user_id: int,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        添加文档到向量存储
        
        Args:
            user_id: 用户ID
            texts: 文档文本列表
            metadatas: 文档元数据列表
            ids: 文档ID列表
            
        Returns:
            是否添加成功
        """
        try:
            vectorstore = self.get_user_vectorstore(user_id)
            
            # 如果没有提供 ids，自动生成
            if ids is None:
                ids = [f"doc_{user_id}_{i}" for i in range(len(texts))]
            
            # 使用 LangChain 的 add_texts 方法（会自动向量化）
            vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def search(
        self,
        user_id: int,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        在向量存储中进行相似度检索
        
        Args:
            user_id: 用户ID
            query: 查询文本
            n_results: 返回结果数量
            filter_metadata: 元数据过滤条件
            
        Returns:
            检索结果字典
        """
        try:
            vectorstore = self.get_user_vectorstore(user_id)
            
            # 使用 similarity_search_with_relevance_scores 方法
            # 获取文档和相似度分数
            filter_dict = filter_metadata if filter_metadata else None
            
            results = vectorstore.similarity_search_with_relevance_scores(
                query=query,
                k=n_results,
                filter=filter_dict
            )
            
            # 格式化结果
            documents = []
            metadatas = []
            distances = []
            doc_ids = []
            
            for doc, score in results:
                documents.append(doc.page_content)
                metadatas.append(doc.metadata)
                distances.append(1 - score)  # 将相似度转换为距离
                doc_ids.append(doc.metadata.get("chunk_id", ""))
            
            return {
                "documents": [documents],
                "metadatas": [metadatas],
                "distances": [distances],
                "ids": [doc_ids]
            }
        except Exception as e:
            print(f"Error searching documents: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
    
    def as_retriever(
        self,
        user_id: int,
        search_type: str = "similarity",
        search_kwargs: Optional[Dict[str, Any]] = None
    ):
        """
        将向量存储转换为 LangChain Retriever
        
        Args:
            user_id: 用户ID
            search_type: 检索类型（similarity, mmr, similarity_score_threshold）
            search_kwargs: 检索参数（如 k, score_threshold）
            
        Returns:
            LangChain Retriever 对象
        """
        vectorstore = self.get_user_vectorstore(user_id)
        
        if search_kwargs is None:
            search_kwargs = {"k": 5}
        
        return vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )
    
    def delete_documents(
        self,
        user_id: int,
        ids: List[str]
    ) -> bool:
        """
        从向量存储中删除文档
        
        Args:
            user_id: 用户ID
            ids: 要删除的文档ID列表
            
        Returns:
            是否删除成功
        """
        try:
            vectorstore = self.get_user_vectorstore(user_id)
            vectorstore.delete(ids=ids)
            return True
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return False
    
    def update_documents(
        self,
        user_id: int,
        ids: List[str],
        texts: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        更新向量存储中的文档
        
        Args:
            user_id: 用户ID
            ids: 要更新的文档ID列表
            texts: 新的文档文本列表
            metadatas: 新的元数据列表
            
        Returns:
            是否更新成功
        """
        try:
            # Chroma 不支持直接更新，需要先删除再添加
            # 这里实现为删除旧文档，添加新文档
            self.delete_documents(user_id, ids)
            
            if texts:
                self.add_documents(user_id, texts, metadatas, ids)
            
            return True
        except Exception as e:
            print(f"Error updating documents: {e}")
            return False
    
    def get_collection_stats(self, user_id: int) -> Dict[str, int]:
        """
        获取用户向量存储的统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        try:
            vectorstore = self.get_user_vectorstore(user_id)
            # 通过检索获取文档数量
            # 注意：Chroma 没有直接的 count 方法，需要通过其他方式获取
            collection = vectorstore._collection
            count = collection.count()
            
            return {
                "user_id": user_id,
                "count": count
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {"user_id": user_id, "count": 0}
    
    def delete_user_collection(self, user_id: int) -> bool:
        """
        删除用户的向量存储
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        try:
            collection_name = f"user_{user_id}"
            
            # 删除集合
            vectorstore = self.get_user_vectorstore(user_id)
            vectorstore.delete_collection()
            
            # 清除缓存
            if user_id in self._user_vectorstores:
                del self._user_vectorstores[user_id]
            
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False


# 全局向量数据库实例（单例模式）
_vector_db_instance: Optional[VectorDatabase] = None


def get_vector_db() -> VectorDatabase:
    """
    获取全局向量数据库实例（单例模式）
    
    Returns:
        VectorDatabase 实例
    """
    global _vector_db_instance
    if _vector_db_instance is None:
        _vector_db_instance = VectorDatabase()
    return _vector_db_instance
