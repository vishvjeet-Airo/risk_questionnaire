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


def run_qdrant_filtering_tests():
    """Run Qdrant filtering tests."""
    print("\n" + "=" * 60)
    print("Running Qdrant Filtering Tests")
    print("=" * 60)
    from app.tests.test_qdrant_filtering import TestQdrantFiltering
    
    test_instance = TestQdrantFiltering()
    
    try:
        # Setup test data first
        print("\nStep 1: Setting up test data...")
        if not test_instance.setup_test_data():
            print("\n❌ Failed to setup test data. Exiting.")
            return
        
        print("\nStep 2: Running filtering tests...\n")
        
        test_instance.test_search_without_filters()
        print()
        
        test_instance.test_search_with_sector_filter()
        print()
        
        test_instance.test_search_with_technology_filter()
        print()
        
        test_instance.test_search_with_both_filters()
        print()
        
        test_instance.test_search_with_multiple_sectors()
        print()
        
        test_instance.test_search_with_multiple_technologies()
        print()
        
        test_instance.test_search_with_multiple_filters()
        print()
        
        test_instance.test_search_with_nonexistent_filter()
        print()
        
        test_instance.test_search_with_empty_filters()
        print()
        
        test_instance.test_specific_query_with_filters()
        print()
        
        print("\n✓ All Qdrant filtering tests passed!")
        print("\nNote: Test data has been inserted into Qdrant.")
        print("      You may want to clean up the test data if needed.")
    except Exception as e:
        print(f"\n✗ Qdrant filtering tests failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    # Check if specific test is requested
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == "bedrock":
            run_bedrock_tests()
        elif test_type == "qdrant":
            run_qdrant_tests()
        elif test_type == "filtering":
            run_qdrant_filtering_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available: bedrock, qdrant, filtering")
    else:
        # Run all tests
        run_bedrock_tests()
        run_qdrant_tests()
        
        # Note: Filtering tests are not run by default as they insert test data
        # Uncomment the line below to include them:
        # run_qdrant_filtering_tests()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nTo run filtering tests separately, use:")
    print("  python -m app.tests.run_tests filtering")
    print("  or")
    print("  python app/tests/test_qdrant_filtering.py")
