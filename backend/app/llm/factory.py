import os
from enum import Enum
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_core.language_models import BaseChatModel

class LLMProvider(str, Enum):
    """支持的LLM提供商"""
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_REASONER = "deepseek-reasoner"
    GLM_4_7 = "glm-4.7"
    GLM_4 = "glm-4"
    GLM_3_TURBO = "glm-3-turbo"

class EmbeddingProvider(str, Enum):
    """支持的Embedding提供商"""
    ZHIPUAI_EMBEDDING_3 = "embedding-3"

class LLMFactory:
    """LLM工厂类，用于创建各种AI模型实例"""
    
    @staticmethod
    def create_chat_model(
        provider: LLMProvider,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = False
    ) -> BaseChatModel:
        """
        创建对话模型
        
        Args:
            provider: LLM提供商枚举
            temperature: 采样温度 (0.0-2.0)
            max_tokens: 最大生成长度
            streaming: 是否启用流式输出
            
        Returns:
            BaseChatModel: LangChain对话模型实例
        """
        if provider in [LLMProvider.DEEPSEEK_CHAT, LLMProvider.DEEPSEEK_REASONER]:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
            
            return ChatOpenAI(
                model=provider.value,
                openai_api_key=api_key,
                openai_api_base="https://api.deepseek.com/v1",
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=streaming
            )
        elif provider in [LLMProvider.GLM_4_7, LLMProvider.GLM_4, LLMProvider.GLM_3_TURBO]:
            api_key = os.getenv("ZHIPUAI_API_KEY")
            if not api_key:
                raise ValueError("ZHIPUAI_API_KEY environment variable is not set")
            
            return ChatZhipuAI(
                model=provider.value,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=streaming
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
    @staticmethod
    def create_embeddings(
        provider: EmbeddingProvider = EmbeddingProvider.ZHIPUAI_EMBEDDING_3
    ) -> ZhipuAIEmbeddings:
        """
        创建Embedding模型
        
        Args:
            provider: Embedding提供商枚举
            
        Returns:
            ZhipuAIEmbeddings: 智谱AI Embedding实例
        """
        if provider != EmbeddingProvider.ZHIPUAI_EMBEDDING_3:
            raise ValueError(f"Unsupported embedding provider: {provider}")
        
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable is not set")
        
        return ZhipuAIEmbeddings(
            api_key=api_key,
            model=provider.value
        )
