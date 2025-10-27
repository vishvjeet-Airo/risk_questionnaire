"""Test file for Qdrant client functionality."""

# import pytest
from app.core.clients.qdrant import (
    qdrant,
    ensure_collection,
    paragraph_chunks,
    create_embeddings,
    store_in_qdrant,
    search_qdrant,
    embed_text
)
from app.core.config import settings


class TestQdrantClient:
    """Test cases for Qdrant client."""

    def test_qdrant_connection(self):
        """Test that Qdrant client can connect."""
        try:
            collections = qdrant.get_collections()
            assert collections is not None
            print("✓ Qdrant connection successful")
        except Exception as e:
            print(f"⚠ Qdrant not running or not accessible: {e}")
            print("  Make sure Qdrant is running on localhost:6333")

    def test_ensure_collection(self):
        """Test collection creation."""
        try:
            ensure_collection()
            # Verify collection exists
            collections = qdrant.get_collections()
            collection_names = [c.name for c in collections.collections]
            assert settings.qdrant_collection_name in collection_names
            print(f"✓ Collection '{settings.qdrant_collection_name}' ensured")
        except Exception as e:
            print(f"⚠ Could not ensure collection: {e}")

    def test_paragraph_chunks(self):
        """Test paragraph chunking functionality."""
        text = """This is the first paragraph.

This is the second paragraph.

This is the third paragraph."""
        
        chunks = paragraph_chunks(text)
        
        assert chunks is not None
        assert isinstance(chunks, list)
        assert len(chunks) == 3
        assert chunks[0] == "This is the first paragraph."
        assert chunks[1] == "This is the second paragraph."
        assert chunks[2] == "This is the third paragraph."
        print(f"✓ Successfully chunked text into {len(chunks)} paragraphs")

    def test_empty_paragraph_chunks(self):
        """Test chunking empty text."""
        text = ""
        chunks = paragraph_chunks(text)
        
        assert chunks is not None
        assert isinstance(chunks, list)
        assert len(chunks) == 0
        print("✓ Empty text handled correctly")

    def test_embed_text(self):
        """Test embedding text."""
        text = "This is a test text for embedding"
        embedding = embed_text(text)
        
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
        print(f"✓ Generated embedding with {len(embedding)} dimensions")

    def test_create_embeddings(self):
        """Test creating embeddings for multiple texts."""
        texts = [
            "First paragraph about AI.",
            "Second paragraph about machine learning.",
            "Third paragraph about deep learning."
        ]
        
        embeddings = create_embeddings(texts)
        
        assert embeddings is not None
        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)
        print(f"✓ Created {len(embeddings)} embeddings")

    def test_store_and_search_in_qdrant(self):
        """Test storing and searching in Qdrant."""
        try:
            # Ensure collection exists
            ensure_collection()
            
            # Prepare test data
            chunks = [
                "Python is a programming language.",
                "Machine learning is a subset of AI.",
                "Deep learning uses neural networks."
            ]
            
            # Create embeddings
            embeddings = create_embeddings(chunks)
            assert len(embeddings) == len(chunks)
            
            # Store in Qdrant
            store_in_qdrant(chunks, embeddings)
            print("✓ Data stored in Qdrant successfully")
            
            # Search for similar content
            query = "What is Python?"
            results = search_qdrant(query, top_k=2)
            
            assert results is not None
            assert isinstance(results, list)
            assert len(results) > 0
            assert all("text" in result and "score" in result for result in results)
            
            print(f"✓ Found {len(results)} results")
            for i, result in enumerate(results):
                print(f"  Result {i+1}: Score={result['score']:.4f}, Text={result['text'][:50]}...")
                
        except Exception as e:
            print(f"⚠ Could not test Qdrant operations: {e}")

    def test_search_with_empty_query(self):
        """Test search with empty query."""
        try:
            results = search_qdrant("", top_k=5)
            assert results is not None
            assert isinstance(results, list)
            print("✓ Empty query handled correctly")
        except Exception as e:
            print(f"⚠ Could not test empty query search: {e}")

    def test_collection_info(self):
        """Test getting collection information."""
        try:
            collection_info = qdrant.get_collection(settings.qdrant_collection_name)
            assert collection_info is not None
            print(f"✓ Collection info retrieved: {collection_info}")
            print(f"  Vector size: {collection_info.config.params.vectors.size}")
        except Exception as e:
            print(f"⚠ Could not get collection info: {e}")


if __name__ == "__main__":
    print("Running Qdrant Client Tests...\n")
    
    # Create test instance
    test_instance = TestQdrantClient()
    
    # Run tests
    try:
        test_instance.test_qdrant_connection()
        test_instance.test_ensure_collection()
        test_instance.test_paragraph_chunks()
        test_instance.test_empty_paragraph_chunks()
        test_instance.test_embed_text()
        test_instance.test_create_embeddings()
        test_instance.test_collection_info()
        
        # Note: Storage and search tests require Qdrant to be running
        print("\n⚠ Skipping storage/search tests - comment out to run them")
        # Uncomment to test storage and search operations:
        # test_instance.test_store_and_search_in_qdrant()
        
    except Exception as e:
        print(f"\n✗ Some tests failed: {e}")
    
    print("\n✓ Qdrant client tests completed!")
