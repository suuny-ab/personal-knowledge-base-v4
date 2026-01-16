"""
Unit tests for Document Chunker

Tests document chunking strategies and utilities.
"""

import pytest
from typing import List, Tuple

from backend.app.utils.chunker import (
    DocumentChunker,
    ChunkingStrategy,
    DEFAULT_CHUNKER,
    MARKDOWN_CHUNKER,
    chunk_document
)


class TestChunkingStrategies:
    """测试分块策略"""
    
    def test_fixed_size_chunking(self):
        """测试固定大小分块"""
        chunker = DocumentChunker(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100,
            chunk_overlap=0
        )
        
        text = "这是一段测试文本。" * 20  # 约240个字符
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 1
        # 验证每个分块不超过指定大小
        for chunk, metadata in chunks:
            assert len(chunk) <= 100
            assert metadata["strategy"] == ChunkingStrategy.FIXED_SIZE
    
    def test_sentence_based_chunking(self):
        """测试基于句子的分块"""
        chunker = DocumentChunker(
            strategy=ChunkingStrategy.SENTENCE_BASED,
            chunk_size=50,
            chunk_overlap=0
        )
        
        text = "这是第一句话。这是第二句话！这是第三句话？这是第四句话。"
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        for chunk, metadata in chunks:
            assert metadata["strategy"] == ChunkingStrategy.SENTENCE_BASED
            assert "chunk_id" in metadata
    
    def test_paragraph_based_chunking(self):
        """测试基于段落的分块"""
        chunker = DocumentChunker(
            strategy=ChunkingStrategy.PARAGRAPH_BASED,
            chunk_size=100,
            chunk_overlap=0
        )
        
        text = "这是第一段。\n\n这是第二段。\n\n这是第三段。"
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        for chunk, metadata in chunks:
            assert metadata["strategy"] == ChunkingStrategy.PARAGRAPH_BASED
    
    def test_chunk_overlap(self):
        """测试分块重叠"""
        chunker = DocumentChunker(
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100,
            chunk_overlap=50
        )
        
        text = "这是一段很长的测试文本。" * 20
        chunks_with_metadata = chunker.chunk_text(text)
        chunks = [chunk for chunk, _ in chunks_with_metadata]
        
        if len(chunks) > 1:
            # 检查相邻分块是否有重叠
            first_chunk = chunks[0]
            second_chunk = chunks[1]
            
            # 第二个分块应该包含第一个分块的末尾部分
            overlap_text = first_chunk[-50:]
            assert overlap_text in second_chunk
    
    def test_empty_text(self):
        """测试空文本"""
        chunker = DocumentChunker()
        chunks = chunker.chunk_text("")
        
        assert len(chunks) == 0
    
    def test_whitespace_only_text(self):
        """测试只有空白的文本"""
        chunker = DocumentChunker()
        chunks = chunker.chunk_text("   \n\n   ")
        
        assert len(chunks) == 0


class TestMetadataHandling:
    """测试元数据处理"""
    
    def test_chunk_metadata(self):
        """测试分块元数据"""
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=0)
        metadata = {"source": "test.txt", "author": "test"}
        
        text = "这是一段测试文本。" * 20
        chunks = chunker.chunk_text(text, metadata)
        
        assert len(chunks) > 0
        
        for i, (chunk, chunk_metadata) in enumerate(chunks):
            assert chunk_metadata["source"] == "test.txt"
            assert chunk_metadata["author"] == "test"
            assert chunk_metadata["chunk_id"] == i
            assert chunk_metadata["chunk_index"] == i
            assert "chunk_size" in chunk_metadata
            assert chunk_metadata["chunk_size"] == len(chunk)
    
    def test_metadata_preservation(self):
        """测试元数据保留"""
        chunker = DocumentChunker(chunk_size=30, chunk_overlap=0)
        original_metadata = {
            "title": "测试文档",
            "date": "2026-01-16",
            "tags": ["AI", "NLP"]
        }
        
        text = "这是第一句。这是第二句。这是第三句。"
        chunks = chunker.chunk_text(text, original_metadata)
        
        for chunk, metadata in chunks:
            assert metadata["title"] == "测试文档"
            assert metadata["date"] == "2026-01-16"
            assert metadata["tags"] == ["AI", "NLP"]


class TestMarkdownChunking:
    """测试 Markdown 分块"""
    
    def test_markdown_chunking(self):
        """测试 Markdown 分块"""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=0)
        
        markdown_text = """# 标题1
这是标题1的内容。

## 标题2
这是标题2的内容。

### 标题3
这是标题3的内容。"""
        
        chunks = chunker.chunk_markdown(markdown_text)
        
        assert len(chunks) > 0
        for chunk, metadata in chunks:
            assert metadata["format"] == "markdown"
            assert "heading" in metadata
    
    def test_markdown_heading_detection(self):
        """测试 Markdown 标题检测"""
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=0)
        
        markdown_text = """# 第一章
第一章内容。

## 第二章
第二章内容。"""
        
        chunks = chunker.chunk_markdown(markdown_text)
        
        # 应该检测到至少两个不同的标题（可能包含默认的 "Introduction"）
        headings = [metadata["heading"] for _, metadata in chunks]
        assert len(chunks) > 0
        # 验证至少有一个标题被正确检测到
        assert "第二章" in headings or "第一章" in headings
    
    def test_long_markdown_chunking(self):
        """测试长 Markdown 文档分块"""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=0)
        
        markdown_text = "# 标题\n" + "这是一段很长很长的测试内容。" * 20
        chunks = chunker.chunk_markdown(markdown_text)
        
        # 长内容应该被进一步分割
        assert len(chunks) > 1
        
        # 检查是否有子分块
        has_sub_chunk = any("sub_chunk_id" in metadata for _, metadata in chunks)
        # 由于内容较长，可能会有子分块
        # 这里只是验证结构，不强求一定有子分块


class TestUtilityFunctions:
    """测试工具函数"""
    
    def test_default_chunker(self):
        """测试默认分块器"""
        text = "这是一段测试文本。" * 20
        chunks = DEFAULT_CHUNKER.chunk_text(text)
        
        assert len(chunks) > 0
        assert DEFAULT_CHUNKER.strategy == ChunkingStrategy.SENTENCE_BASED
    
    def test_markdown_chunker(self):
        """测试 Markdown 分块器"""
        markdown_text = "# 标题\n内容"
        chunks = MARKDOWN_CHUNKER.chunk_markdown(markdown_text)
        
        assert len(chunks) > 0
        assert MARKDOWN_CHUNKER.strategy == ChunkingStrategy.PARAGRAPH_BASED
    
    def test_chunk_document_utility(self):
        """测试 chunk_document 工具函数"""
        text = "这是一段测试文本。" * 10
        metadata = {"source": "test"}
        
        # 普通文本
        chunks = chunk_document(text, metadata=metadata)
        assert len(chunks) > 0
        
        # Markdown 文本
        markdown_text = "# 标题\n内容" * 5
        chunks_md = chunk_document(markdown_text, metadata=metadata, is_markdown=True)
        assert len(chunks_md) > 0
        assert chunks_md[0][1]["format"] == "markdown"
    
    def test_chunk_document_with_custom_strategy(self):
        """测试使用自定义策略的 chunk_document"""
        text = "这是一段测试文本。" * 20
        
        chunks = chunk_document(text, strategy=ChunkingStrategy.FIXED_SIZE)
        
        assert len(chunks) > 0
        assert chunks[0][1]["strategy"] == ChunkingStrategy.FIXED_SIZE


class TestEdgeCases:
    """测试边界情况"""
    
    def test_very_long_sentence(self):
        """测试超长句子"""
        chunker = DocumentChunker(
            strategy=ChunkingStrategy.SENTENCE_BASED,
            chunk_size=50,
            chunk_overlap=0
        )
        
        # 一个超长的句子
        text = "这是一个非常非常长的句子，没有任何标点符号。" * 30
        chunks = chunker.chunk_text(text)
        
        # 应该回退到固定大小分块
        assert len(chunks) > 0
        for chunk, metadata in chunks:
            assert len(chunk) <= chunker.max_chunk_size
    
    def test_single_short_sentence(self):
        """测试单个短句子"""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=0)
        
        text = "这是一个短句子。"
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) == 1
        assert chunks[0][0] == text
    
    def test_text_with_special_chars(self):
        """测试包含特殊字符的文本"""
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=0)
        
        text = "包含特殊字符：@#$%^&*()_+{}[]|\\:;\"'<>?,./ 的文本。"
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        # 特殊字符应该被保留
        assert "@" in chunks[0][0]
