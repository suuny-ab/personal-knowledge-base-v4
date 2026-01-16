"""
ChromaDB 向量数据库配置

实现用户隔离的向量存储系统，支持文档向量化和检索。
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from chromadb.config import Settings
from chromadb import Client as ChromaClient
from chromadb.utils import embedding_functions

from backend.app.llm.factory import LLMFactory, EmbeddingProvider


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
        
        # 初始化 ChromaDB 客户端
        self.client = ChromaClient(
            settings=Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(self.persist_directory)
            )
        )
        
        # 获取 embedding 函数
        self.embeddings = LLMFactory.create_embeddings(provider=embedding_provider)
        
        # 缓存用户集合
        self._user_collections: Dict[int, Any] = {}
    
    def get_user_collection(self, user_id: int) -> Any:
        """
        获取或创建用户的向量集合
        
        Args:
            user_id: 用户ID
            
        Returns:
            Chroma Collection 对象
        """
        if user_id in self._user_collections:
            return self._user_collections[user_id]
        
        collection_name = f"user_{user_id}"
        
        # 尝试获取已存在的集合
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            # 集合不存在，创建新集合
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"user_id": user_id}
            )
        
        self._user_collections[user_id] = collection
        return collection
    
    def add_documents(
        self,
        user_id: int,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        添加文档到向量集合
        
        Args:
            user_id: 用户ID
            documents: 文档文本列表
            metadatas: 文档元数据列表
            ids: 文档ID列表
            
        Returns:
            是否添加成功
        """
        try:
            collection = self.get_user_collection(user_id)
            
            # 如果没有提供 ids，自动生成
            if ids is None:
                ids = [f"doc_{user_id}_{i}" for i in range(len(documents))]
            
            # 添加文档到集合（ChromaDB 会自动使用 embeddings 向量化）
            collection.add(
                documents=documents,
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
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        在用户集合中进行向量检索
        
        Args:
            user_id: 用户ID
            query: 查询文本
            n_results: 返回结果数量
            where: 元数据过滤条件
            
        Returns:
            检索结果字典
        """
        try:
            collection = self.get_user_collection(user_id)
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return {"documents": [], "metadatas": [], "distances": [], "ids": []}
    
    def delete_documents(
        self,
        user_id: int,
        ids: List[str]
    ) -> bool:
        """
        从用户集合中删除文档
        
        Args:
            user_id: 用户ID
            ids: 要删除的文档ID列表
            
        Returns:
            是否删除成功
        """
        try:
            collection = self.get_user_collection(user_id)
            collection.delete(ids=ids)
            return True
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return False
    
    def update_documents(
        self,
        user_id: int,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        更新用户集合中的文档
        
        Args:
            user_id: 用户ID
            ids: 要更新的文档ID列表
            documents: 新的文档文本列表
            metadatas: 新的元数据列表
            
        Returns:
            是否更新成功
        """
        try:
            collection = self.get_user_collection(user_id)
            collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            print(f"Error updating documents: {e}")
            return False
    
    def get_collection_stats(self, user_id: int) -> Dict[str, int]:
        """
        获取用户集合的统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        try:
            collection = self.get_user_collection(user_id)
            return {
                "user_id": user_id,
                "count": collection.count()
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {"user_id": user_id, "count": 0}
    
    def delete_user_collection(self, user_id: int) -> bool:
        """
        删除用户的向量集合
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        try:
            collection_name = f"user_{user_id}"
            self.client.delete_collection(name=collection_name)
            
            # 清除缓存
            if user_id in self._user_collections:
                del self._user_collections[user_id]
            
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False
    
    def list_user_collections(self) -> List[str]:
        """
        列出所有用户集合名称
        
        Returns:
            用户集合名称列表
        """
        try:
            collections = self.client.list_collections()
            return [collection.name for collection in collections]
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []


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
