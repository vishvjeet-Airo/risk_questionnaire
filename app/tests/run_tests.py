"""Simple test runner for client tests."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def run_bedrock_tests():
    """Run Bedrock client tests."""
    print("=" * 60)
    print("Running Bedrock Client Tests")
    print("=" * 60)
    from app.tests.test_bedrock_client import TestBedrockClient
    
    test_instance = TestBedrockClient()
    
    try:
        test_instance.test_client_initialization()
        test_instance.test_embed_text()
        test_instance.test_embed_texts()
        test_instance.test_invoke_with_tracing()
        test_instance.test_invoke_with_system_message()
        test_instance.test_embedding_dimensions_consistency()
        print("\n✓ All Bedrock client tests passed!")
    except Exception as e:
        print(f"\n✗ Bedrock tests failed: {e}")
        import traceback
        traceback.print_exc()


def run_qdrant_tests():
    """Run Qdrant client tests."""
    print("\n" + "=" * 60)
    print("Running Qdrant Client Tests")
    print("=" * 60)
    from app.tests.test_qdrant_client import TestQdrantClient
    
    test_instance = TestQdrantClient()
    
    try:
        test_instance.test_qdrant_connection()
        test_instance.test_ensure_collection()
        test_instance.test_paragraph_chunks()
        test_instance.test_empty_paragraph_chunks()
        test_instance.test_embed_text()
        test_instance.test_create_embeddings()
        test_instance.test_collection_info()
        print("\n✓ All Qdrant client tests passed!")
    except Exception as e:
        print(f"\n✗ Qdrant tests failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run all tests
    run_bedrock_tests()
    run_qdrant_tests()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
