"""Test file for Bedrock client functionality."""

# import pytest
from app.core.clients.bedrock import bedrock_client


class TestBedrockClient:
    """Test cases for Bedrock client."""

    def test_client_initialization(self):
        """Test that the bedrock client is initialized correctly."""
        assert bedrock_client is not None
        assert bedrock_client.client is not None
        assert bedrock_client.embedding_client is not None
        print("✓ Bedrock client initialized successfully")

    def test_embed_text(self):
        """Test embedding a single text."""
        text = "This is a test embedding"
        embedding = bedrock_client.embed_text(text)
        
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
        print(f"✓ Generated embedding with {len(embedding)} dimensions")

    def test_embed_texts(self):
        """Test embedding multiple texts."""
        texts = [
            "First text to embed",
            "Second text to embed",
            "Third text to embed"
        ]
        embeddings = bedrock_client.embed_texts(texts)
        
        assert embeddings is not None
        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)
        print(f"✓ Generated {len(embeddings)} embeddings")

    def test_invoke_with_tracing(self):
        """Test invoking the bedrock model with tracing."""
        prompt = "What is the capital of France?"
        response = bedrock_client.invoke_with_tracing(prompt)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"✓ Received response: {response[:100]}...")

    def test_invoke_with_system_message(self):
        """Test invoking the model with a system message."""
        prompt = "Count from 1 to 5"
        system_message = "You are a helpful assistant that provides concise answers."
        
        response = bedrock_client.invoke_with_tracing(
            prompt=prompt,
            system_message=system_message
        )
        
        assert response is not None
        assert isinstance(response, str)
        print(f"✓ Received response with system message: {response[:100]}...")

    def test_embedding_dimensions_consistency(self):
        """Test that all embeddings have consistent dimensions."""
        texts = ["One", "Two", "Three"]
        embeddings = bedrock_client.embed_texts(texts)
        
        # All embeddings should have the same dimension
        dim = len(embeddings[0])
        assert all(len(emb) == dim for emb in embeddings)
        print(f"✓ All embeddings have consistent dimensions: {dim}")

    def test_empty_text_embedding(self):
        """Test embedding an empty string."""
        text = ""
        embedding = bedrock_client.embed_text(text)
        
        assert embedding is not None
        assert isinstance(embedding, list)
        print(f"✓ Empty text embedded with {len(embedding)} dimensions")


if __name__ == "__main__":
    print("Running Bedrock Client Tests...\n")
    
    # Create test instance
    test_instance = TestBedrockClient()
    
    # Run tests
    test_instance.test_client_initialization()
    test_instance.test_embed_text()
    test_instance.test_embed_texts()
    test_instance.test_invoke_with_tracing()
    test_instance.test_invoke_with_system_message()
    test_instance.test_embedding_dimensions_consistency()
    
    print("\n✓ All Bedrock client tests passed!")
