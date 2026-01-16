"""
文档分块工具

实现智能文档分块策略，支持固定大小、语义段落等多种分块方式。
"""

from typing import List, Optional, Tuple
from enum import Enum
import re


class ChunkingStrategy(str, Enum):
    """分块策略枚举"""
    FIXED_SIZE = "fixed_size"           # 固定大小分块
    SENTENCE_BASED = "sentence_based"   # 基于句子的分块
    PARAGRAPH_BASED = "paragraph_based" # 基于段落的分块
    SEMANTIC = "semantic"               # 语义分块（预留接口）


class DocumentChunker:
    """文档分块工具类"""
    
    def __init__(
        self,
        strategy: ChunkingStrategy = ChunkingStrategy.SENTENCE_BASED,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        max_chunk_size: int = 1000
    ):
        """
        初始化文档分块器
        
        Args:
            strategy: 分块策略
            chunk_size: 目标分块大小（字符数）
            chunk_overlap: 分块重叠大小（字符数）
            max_chunk_size: 最大分块大小（防止过长）
        """
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunk_size = max_chunk_size
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[dict] = None
    ) -> List[Tuple[str, dict]]:
        """
        对文本进行分块
        
        Args:
            text: 要分块的文本
            metadata: 文档元数据
            
        Returns:
            分块结果列表，每个元素为 (text, metadata) 元组
        """
        if not text or not text.strip():
            return []
        
        # 清理文本
        text = self._clean_text(text)
        
        # 根据策略选择分块方法
        if self.strategy == ChunkingStrategy.FIXED_SIZE:
            chunks = self._chunk_fixed_size(text)
        elif self.strategy == ChunkingStrategy.SENTENCE_BASED:
            chunks = self._chunk_by_sentences(text)
        elif self.strategy == ChunkingStrategy.PARAGRAPH_BASED:
            chunks = self._chunk_by_paragraphs(text)
        elif self.strategy == ChunkingStrategy.SEMANTIC:
            # 语义分块预留接口，暂时使用句子分块
            chunks = self._chunk_by_sentences(text)
        else:
            chunks = self._chunk_by_sentences(text)
        
        # 添加元数据
        result = []
        base_metadata = metadata or {}
        
        for i, chunk_text in enumerate(chunks):
            chunk_metadata = {
                **base_metadata,
                "chunk_id": i,
                "chunk_index": i,
                "strategy": self.strategy,
                "chunk_size": len(chunk_text)
            }
            result.append((chunk_text, chunk_metadata))
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 移除行首尾空格
        text = '\n'.join(line.strip() for line in text.split('\n'))
        return text.strip()
    
    def _chunk_fixed_size(self, text: str) -> List[str]:
        """
        固定大小分块
        
        Args:
            text: 文本
            
        Returns:
            分块列表
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            
            # 确保不超过最大大小
            if end > start + self.max_chunk_size:
                end = start + self.max_chunk_size
            
            chunk = text[start:end]
            chunks.append(chunk)
            
            # 移动到下一个分块（考虑重叠）
            start = end - self.chunk_overlap
        
        return chunks
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """
        基于句子的分块
        
        Args:
            text: 文本
            
        Returns:
            分块列表
        """
        # 使用正则表达式分割句子
        sentences = re.split(r'([。！？.!?]+\s*)', text)
        
        # 重新组合句子和标点
        sentence_list = []
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i] + sentences[i + 1]
            if sentence.strip():
                sentence_list.append(sentence)
        
        # 如果最后一个句子没有标点，也加上
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            sentence_list.append(sentences[-1])
        
        # 将句子合并为分块
        chunks = []
        current_chunk = ""
        
        for sentence in sentence_list:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        # 如果分块太少，回退到固定大小分块
        if len(chunks) == 0 or (len(chunks) == 1 and len(chunks[0]) > self.chunk_size):
            return self._chunk_fixed_size(text)
        
        return chunks
    
    def _chunk_by_paragraphs(self, text: str) -> List[str]:
        """
        基于段落的分块
        
        Args:
            text: 文本
            
        Returns:
            分块列表
        """
        # 按空行分割段落
        paragraphs = text.split('\n\n')
        
        # 清理空段落
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # 如果没有段落，回退到句子分块
        if not paragraphs:
            return self._chunk_by_sentences(text)
        
        # 将段落合并为分块
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= self.chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # 如果分块太少，回退到句子分块
        if len(chunks) == 0:
            return self._chunk_by_sentences(text)
        
        # 检查是否有超长的分块
        for i, chunk in enumerate(chunks):
            if len(chunk) > self.max_chunk_size:
                # 对超长段落进行二次分块
                chunks[i:i+1] = self._chunk_by_sentences(chunk)
        
        return chunks
    
    def chunk_markdown(self, markdown_text: str, metadata: Optional[dict] = None) -> List[Tuple[str, dict]]:
        """
        专门针对 Markdown 文本进行分块，保留结构信息
        
        Args:
            markdown_text: Markdown 文本
            metadata: 文档元数据
            
        Returns:
            分块结果列表
        """
        # 简单实现：按标题分割
        lines = markdown_text.split('\n')
        chunks = []
        current_chunk = []
        current_heading = "Introduction"
        base_metadata = metadata or {}
        
        for line in lines:
            # 检测标题（# 开头）
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if heading_match and current_chunk:
                # 保存当前分块
                chunk_text = '\n'.join(current_chunk).strip()
                chunk_metadata = {
                    **base_metadata,
                    "heading": current_heading,
                    "format": "markdown"
                }
                chunks.append((chunk_text, chunk_metadata))
                current_chunk = []
                current_heading = heading_match.group(2)
            
            current_chunk.append(line)
        
        # 添加最后一个分块
        if current_chunk:
            chunk_text = '\n'.join(current_chunk).strip()
            chunk_metadata = {
                **base_metadata,
                "heading": current_heading,
                "format": "markdown"
            }
            chunks.append((chunk_text, chunk_metadata))
        
        # 对每个分块进行进一步分块（如果过长）
        final_chunks = []
        for chunk_text, chunk_metadata in chunks:
            if len(chunk_text) > self.chunk_size:
                sub_chunks = self._chunk_by_sentences(chunk_text)
                for i, sub_chunk in enumerate(sub_chunks):
                    final_chunks.append((sub_chunk, {**chunk_metadata, "sub_chunk_id": i}))
            else:
                final_chunks.append((chunk_text, chunk_metadata))
        
        return final_chunks


# 预设的分块器实例
DEFAULT_CHUNKER = DocumentChunker(
    strategy=ChunkingStrategy.SENTENCE_BASED,
    chunk_size=500,
    chunk_overlap=50
)

MARKDOWN_CHUNKER = DocumentChunker(
    strategy=ChunkingStrategy.PARAGRAPH_BASED,
    chunk_size=800,
    chunk_overlap=100
)


def chunk_document(
    text: str,
    strategy: Optional[ChunkingStrategy] = None,
    metadata: Optional[dict] = None,
    is_markdown: bool = False
) -> List[Tuple[str, dict]]:
    """
    便捷函数：对文档进行分块
    
    Args:
        text: 文档文本
        strategy: 分块策略（默认使用句子分块）
        metadata: 文档元数据
        is_markdown: 是否为 Markdown 格式
        
    Returns:
        分块结果列表
    """
    if is_markdown:
        return MARKDOWN_CHUNKER.chunk_markdown(text, metadata)
    elif strategy:
        chunker = DocumentChunker(strategy=strategy)
        return chunker.chunk_text(text, metadata)
    else:
        return DEFAULT_CHUNKER.chunk_text(text, metadata)
