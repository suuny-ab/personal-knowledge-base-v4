"""
向量存储服务

整合 ChromaDB 向量数据库和文档分块，提供完整的向量存储和检索功能。
"""

from typing import List, Optional, Dict, Any
from pathlib import Path

from backend.app.database.vector_db import VectorDatabase, get_vector_db
from backend.app.utils.chunker import chunk_document, ChunkingStrategy


class VectorService:
    """向量存储服务类"""
    
    def __init__(self, vector_db: Optional[VectorDatabase] = None):
        """
        初始化向量服务
        
        Args:
            vector_db: 向量数据库实例（如果为None，使用全局单例）
        """
        self.vector_db = vector_db or get_vector_db()
    
    def index_document(
        self,
        user_id: int,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunking_strategy: Optional[ChunkingStrategy] = None,
        is_markdown: bool = False
    ) -> Dict[str, Any]:
        """
        索引文档到向量数据库
        
        Args:
            user_id: 用户ID
            text: 文档文本
            metadata: 文档元数据
            chunking_strategy: 分块策略
            is_markdown: 是否为Markdown格式
            
        Returns:
            索引结果字典
        """
        # 对文档进行分块
        chunks = chunk_document(
            text=text,
            strategy=chunking_strategy,
            metadata=metadata,
            is_markdown=is_markdown
        )
        
        if not chunks:
            return {
                "success": False,
                "message": "文档为空或分块失败",
                "indexed_chunks": 0
            }
        
        # 提取文本和元数据
        documents = [chunk for chunk, _ in chunks]
        metadatas = [meta for _, meta in chunks]
        
        # 生成文档ID
        base_id = metadata.get("doc_id", "unknown") if metadata else "unknown"
        ids = [f"{base_id}_chunk_{i}" for i in range(len(documents))]
        
        # 添加到向量数据库
        success = self.vector_db.add_documents(
            user_id=user_id,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return {
            "success": success,
            "indexed_chunks": len(documents),
            "message": f"成功索引 {len(documents)} 个文档块" if success else "索引失败"
        }
    
    def index_file(
        self,
        user_id: int,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        索引文件到向量数据库
        
        Args:
            user_id: 用户ID
            file_path: 文件路径
            metadata: 文档元数据
            
        Returns:
            索引结果字典
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "message": f"文件不存在: {file_path}",
                    "indexed_chunks": 0
                }
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 判断是否为 Markdown
            is_markdown = file_path.suffix.lower() in ['.md', '.markdown']
            
            # 添加文件路径到元数据
            base_metadata = metadata or {}
            base_metadata["file_path"] = str(file_path)
            base_metadata["file_name"] = file_path.name
            
            # 索引文档
            return self.index_document(
                user_id=user_id,
                text=text,
                metadata=base_metadata,
                is_markdown=is_markdown
            )
        
        except Exception as e:
            return {
                "success": False,
                "message": f"读取文件失败: {str(e)}",
                "indexed_chunks": 0
            }
    
    def search(
        self,
        user_id: int,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        在向量数据库中进行语义检索
        
        Args:
            user_id: 用户ID
            query: 查询文本
            n_results: 返回结果数量
            filter_metadata: 元数据过滤条件
            
        Returns:
            检索结果字典
        """
        try:
            results = self.vector_db.search(
                user_id=user_id,
                query=query,
                n_results=n_results,
                where=filter_metadata
            )
            
            # 格式化结果
            formatted_results = []
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            ids = results.get("ids", [[]])[0]
            
            for i in range(len(documents)):
                formatted_results.append({
                    "id": ids[i] if i < len(ids) else None,
                    "content": documents[i] if i < len(documents) else None,
                    "metadata": metadatas[i] if i < len(metadatas) else None,
                    "distance": distances[i] if i < len(distances) else None,
                    "similarity": 1 - distances[i] if i < len(distances) else None
                })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "total_results": len(formatted_results)
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"检索失败: {str(e)}",
                "results": [],
                "total_results": 0
            }
    
    def delete_document(
        self,
        user_id: int,
        doc_id: str
    ) -> Dict[str, Any]:
        """
        删除文档（根据文档ID删除所有相关分块）
        
        Args:
            user_id: 用户ID
            doc_id: 文档ID
            
        Returns:
            删除结果字典
        """
        try:
            # 先搜索获取所有相关分块
            results = self.vector_db.search(
                user_id=user_id,
                query="",
                n_results=1000  # 获取所有结果
            )
            
            # 筛选出属于该文档的分块
            ids_to_delete = []
            all_ids = results.get("ids", [[]])[0]
            for chunk_id in all_ids:
                if chunk_id.startswith(f"{doc_id}_chunk_"):
                    ids_to_delete.append(chunk_id)
            
            if not ids_to_delete:
                return {
                    "success": False,
                    "message": f"未找到文档 {doc_id} 的分块",
                    "deleted_chunks": 0
                }
            
            # 删除分块
            success = self.vector_db.delete_documents(
                user_id=user_id,
                ids=ids_to_delete
            )
            
            return {
                "success": success,
                "deleted_chunks": len(ids_to_delete),
                "message": f"成功删除 {len(ids_to_delete)} 个文档块" if success else "删除失败"
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"删除失败: {str(e)}",
                "deleted_chunks": 0
            }
    
    def get_collection_stats(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        获取用户向量集合的统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        try:
            stats = self.vector_db.get_collection_stats(user_id)
            
            return {
                "success": True,
                "user_id": stats["user_id"],
                "total_chunks": stats["count"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"获取统计信息失败: {str(e)}",
                "user_id": user_id,
                "total_chunks": 0
            }
    
    def clear_collection(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        清空用户的向量集合
        
        Args:
            user_id: 用户ID
            
        Returns:
            清空结果字典
        """
        try:
            success = self.vector_db.delete_user_collection(user_id)
            
            return {
                "success": success,
                "message": "清空成功" if success else "清空失败"
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"清空失败: {str(e)}"
            }


# 全局向量服务实例
_vector_service_instance: Optional[VectorService] = None


def get_vector_service() -> VectorService:
    """
    获取全局向量服务实例（单例模式）
    
    Returns:
        VectorService 实例
    """
    global _vector_service_instance
    if _vector_service_instance is None:
        _vector_service_instance = VectorService()
    return _vector_service_instance
