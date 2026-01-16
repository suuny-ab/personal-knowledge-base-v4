"""
RAG 检索链实现

使用 LangChain LCEL (LangChain Expression Language) 实现基于向量检索的问答系统。
"""

from typing import Optional, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from backend.app.llm.factory import LLMFactory, LLMProvider


def format_docs(docs):
    """格式化检索到的文档"""
    return "\n\n".join([doc.page_content for doc in docs])


class RAGChain:
    """RAG 检索问答链"""
    
    def __init__(
        self,
        retriever: BaseRetriever,
        llm: Optional[BaseChatModel] = None,
        llm_provider: LLMProvider = LLMProvider.DEEPSEEK_CHAT,
        top_k: int = 5,
        score_threshold: Optional[float] = None
    ):
        """
        初始化 RAG 链
        
        Args:
            retriever: 向量检索器
            llm: 自定义 LLM 模型（可选）
            llm_provider: LLM 提供商（默认使用 DeepSeek）
            top_k: 检索文档数量
            score_threshold: 相似度阈值（0-1，None 表示不限制）
        """
        self.retriever = retriever
        self.llm = llm or LLMFactory.create_chat_model(llm_provider)
        self.top_k = top_k
        self.score_threshold = score_threshold
        
        # 创建 RAG 提示词模板（中文化）
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的知识库助手。请根据以下背景信息回答用户的问题。

背景信息：
{context}

回答要求：
1. 仅基于提供的背景信息回答，不要编造信息
2. 如果背景信息不足以回答问题，请明确说明
3. 回答要简洁明了，重点突出
4. 必要时可以引用背景信息中的具体内容"""),
            ("user", "{question}")
        ])
        
        # 延迟构建链，第一次使用时再构建
        self._chain = None
    
    def _build_chain(self):
        """构建 LCEL 检索链"""
        if self._chain is None:
            self._chain = (
                {
                    "context": self.retriever | format_docs,
                    "question": RunnablePassthrough()
                }
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
        return self._chain
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        执行检索增强生成查询
        
        Args:
            question: 用户问题
            
        Returns:
            包含答案和来源的字典:
            {
                "answer": str,          # AI 生成的答案
                "source_documents": list,  # 检索到的文档
                "query": str            # 原始问题
            }
        """
        # 先检索文档
        source_documents = self.retriever.invoke(question)
        
        # 执行查询
        chain = self._build_chain()
        answer = chain.invoke(question)
        
        return {
            "answer": answer,
            "source_documents": source_documents,
            "query": question
        }
    
    async def aquery(self, question: str) -> Dict[str, Any]:
        """
        异步执行检索增强生成查询
        
        Args:
            question: 用户问题
            
        Returns:
            包含答案和来源的字典
        """
        # 先检索文档
        source_documents = await self.retriever.ainvoke(question)
        
        # 执行查询
        chain = self._build_chain()
        answer = await chain.ainvoke(question)
        
        return {
            "answer": answer,
            "source_documents": source_documents,
            "query": question
        }
    
    def get_retriever(self) -> BaseRetriever:
        """获取检索器"""
        return self.retriever
    
    def update_retriever(self, retriever: BaseRetriever):
        """
        更新检索器
        
        Args:
            retriever: 新的检索器
        """
        self.retriever = retriever
        # 重置链，下次查询时重新构建
        self._chain = None


def create_rag_chain(
    retriever: BaseRetriever,
    llm_provider: LLMProvider = LLMProvider.DEEPSEEK_CHAT,
    top_k: int = 5,
    score_threshold: Optional[float] = None
) -> RAGChain:
    """
    创建 RAG 链的工厂函数
    
    Args:
        retriever: 向量检索器
        llm_provider: LLM 提供商
        top_k: 检索文档数量
        score_threshold: 相似度阈值
        
    Returns:
        RAGChain 实例
    """
    return RAGChain(
        retriever=retriever,
        llm_provider=llm_provider,
        top_k=top_k,
        score_threshold=score_threshold
    )
