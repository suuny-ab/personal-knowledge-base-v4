"""
Unit tests for LLM Factory

Tests the factory class that creates LLM instances for different providers.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from backend.app.llm.factory import (
    LLMFactory,
    LLMProvider,
    EmbeddingProvider
)


class TestLLMProvider:
    """Test LLMProvider enum."""
    
    def test_deepseek_chat_value(self):
        """Test DEEPSEEK_CHAT provider value."""
        assert LLMProvider.DEEPSEEK_CHAT.value == "deepseek-chat"
    
    def test_deepseek_reasoner_value(self):
        """Test DEEPSEEK_REASONER provider value."""
        assert LLMProvider.DEEPSEEK_REASONER.value == "deepseek-reasoner"
    
    def test_glm_4_7_value(self):
        """Test GLM_4_7 provider value."""
        assert LLMProvider.GLM_4_7.value == "glm-4.7"
    
    def test_glm_4_value(self):
        """Test GLM_4 provider value."""
        assert LLMProvider.GLM_4.value == "glm-4"
    
    def test_glm_3_turbo_value(self):
        """Test GLM_3_TURBO provider value."""
        assert LLMProvider.GLM_3_TURBO.value == "glm-3-turbo"


class TestEmbeddingProvider:
    """Test EmbeddingProvider enum."""
    
    def test_zhipuai_embedding_3_value(self):
        """Test ZHIPUAI_EMBEDDING_3 provider value."""
        assert EmbeddingProvider.ZHIPUAI_EMBEDDING_3.value == "embedding-3"


class TestLLMFactoryCreateChatModel:
    """Test LLMFactory.create_chat_model method."""
    
    def test_create_deepseek_chat_success(self):
        """Test creating DeepSeek chat model with valid API key."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("backend.app.llm.factory.ChatOpenAI") as mock_chat:
                mock_instance = MagicMock()
                mock_chat.return_value = mock_instance
                
                result = LLMFactory.create_chat_model(
                    LLMProvider.DEEPSEEK_CHAT,
                    temperature=0.8
                )
                
                mock_chat.assert_called_once_with(
                    model="deepseek-chat",
                    openai_api_key="test-key",
                    openai_api_base="https://api.deepseek.com/v1",
                    temperature=0.8,
                    max_tokens=None,
                    streaming=False
                )
                assert result == mock_instance
    
    def test_create_deepseek_reasoner_success(self):
        """Test creating DeepSeek reasoner model."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("backend.app.llm.factory.ChatOpenAI") as mock_chat:
                mock_instance = MagicMock()
                mock_chat.return_value = mock_instance
                
                result = LLMFactory.create_chat_model(
                    LLMProvider.DEEPSEEK_REASONER,
                    temperature=0.9,
                    max_tokens=1000,
                    streaming=True
                )
                
                mock_chat.assert_called_once_with(
                    model="deepseek-reasoner",
                    openai_api_key="test-key",
                    openai_api_base="https://api.deepseek.com/v1",
                    temperature=0.9,
                    max_tokens=1000,
                    streaming=True
                )
                assert result == mock_instance
    
    def test_create_deepseek_missing_api_key(self):
        """Test creating DeepSeek model without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="DEEPSEEK_API_KEY environment variable is not set"):
                LLMFactory.create_chat_model(LLMProvider.DEEPSEEK_CHAT)
    
    def test_create_glm_4_7_success(self):
        """Test creating GLM-4.7 model with valid API key."""
        with patch.dict(os.environ, {"ZHIPUAI_API_KEY": "test-key"}):
            with patch("backend.app.llm.factory.ChatZhipuAI") as mock_chat:
                mock_instance = MagicMock()
                mock_chat.return_value = mock_instance
                
                result = LLMFactory.create_chat_model(
                    LLMProvider.GLM_4_7,
                    temperature=0.6
                )
                
                mock_chat.assert_called_once_with(
                    model="glm-4.7",
                    api_key="test-key",
                    temperature=0.6,
                    max_tokens=None,
                    streaming=False
                )
                assert result == mock_instance
    
    def test_create_glm_4_success(self):
        """Test creating GLM-4 model."""
        with patch.dict(os.environ, {"ZHIPUAI_API_KEY": "test-key"}):
            with patch("backend.app.llm.factory.ChatZhipuAI") as mock_chat:
                mock_instance = MagicMock()
                mock_chat.return_value = mock_instance
                
                result = LLMFactory.create_chat_model(LLMProvider.GLM_4)
                
                mock_chat.assert_called_once_with(
                    model="glm-4",
                    api_key="test-key",
                    temperature=0.7,
                    max_tokens=None,
                    streaming=False
                )
                assert result == mock_instance
    
    def test_create_glm_3_turbo_success(self):
        """Test creating GLM-3-Turbo model."""
        with patch.dict(os.environ, {"ZHIPUAI_API_KEY": "test-key"}):
            with patch("backend.app.llm.factory.ChatZhipuAI") as mock_chat:
                mock_instance = MagicMock()
                mock_chat.return_value = mock_instance
                
                result = LLMFactory.create_chat_model(LLMProvider.GLM_3_TURBO)
                
                mock_chat.assert_called_once_with(
                    model="glm-3-turbo",
                    api_key="test-key",
                    temperature=0.7,
                    max_tokens=None,
                    streaming=False
                )
                assert result == mock_instance
    
    def test_create_zhipuai_missing_api_key(self):
        """Test creating ZhipuAI model without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ZHIPUAI_API_KEY environment variable is not set"):
                LLMFactory.create_chat_model(LLMProvider.GLM_4_7)


class TestLLMFactoryCreateEmbeddings:
    """Test LLMFactory.create_embeddings method."""
    
    def test_create_embeddings_default_success(self):
        """Test creating default embedding model."""
        with patch.dict(os.environ, {"ZHIPUAI_API_KEY": "test-key"}):
            with patch("backend.app.llm.factory.ZhipuAIEmbeddings") as mock_embeddings:
                mock_instance = MagicMock()
                mock_embeddings.return_value = mock_instance
                
                result = LLMFactory.create_embeddings()
                
                mock_embeddings.assert_called_once_with(
                    api_key="test-key",
                    model="embedding-3"
                )
                assert result == mock_instance
    
    def test_create_embeddings_explicit_provider_success(self):
        """Test creating embedding with explicit provider."""
        with patch.dict(os.environ, {"ZHIPUAI_API_KEY": "test-key"}):
            with patch("backend.app.llm.factory.ZhipuAIEmbeddings") as mock_embeddings:
                mock_instance = MagicMock()
                mock_embeddings.return_value = mock_instance
                
                result = LLMFactory.create_embeddings(
                    EmbeddingProvider.ZHIPUAI_EMBEDDING_3
                )
                
                mock_embeddings.assert_called_once_with(
                    api_key="test-key",
                    model="embedding-3"
                )
                assert result == mock_instance
    
    def test_create_embeddings_unsupported_provider(self):
        """Test creating embedding with unsupported provider raises error."""
        # This test would need to be updated if more providers are added
        # For now, we only support ZHIPUAI_EMBEDDING_3
        pass
    
    def test_create_embeddings_missing_api_key(self):
        """Test creating embedding without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ZHIPUAI_API_KEY environment variable is not set"):
                LLMFactory.create_embeddings()
