"""Test file for Qdrant retrieval with filtering by sectors and technologies."""

from app.core.clients.qdrant import (
    qdrant,
    ensure_collection,
    create_embeddings,
    search_qdrant,
    embed_text
)
from qdrant_client.models import PointStruct
from app.core.config import settings
from typing import Optional, List
import uuid


class TestQdrantFiltering:
    """Test cases for Qdrant filtering by sectors and technologies."""

    def setup_test_data(self):
        """Set up test data with different sectors and technologies."""
        try:
            ensure_collection()
            
            # Test data with different sectors and technologies
            test_facts = [
                {
                    "text": "Compass Group uses TaskUp application for task management in the Healthcare sector.",
                    "sectors": ["Healthcare"],
                    "technologies": ["TaskUp"]
                },
                {
                    "text": "Agilysys is used for point-of-sale operations in the Healthcare sector.",
                    "sectors": ["Healthcare"],
                    "technologies": ["Agilysys"]
                },
                {
                    "text": "SquareSpace is used for website management in the Finance sector.",
                    "sectors": ["Finance"],
                    "technologies": ["SquareSpace"]
                },
                {
                    "text": "Triple Seat application handles seating management for Healthcare and Finance sectors.",
                    "sectors": ["Healthcare", "Finance"],
                    "technologies": ["Triple Seat"]
                },
                {
                    "text": "Authorize.net processes payment transactions for Finance sector using multiple technologies.",
                    "sectors": ["Finance"],
                    "technologies": ["Authorize.net", "Payment Processing"]
                },
                {
                    "text": "TaskUp is also used in the Finance sector for project tracking.",
                    "sectors": ["Finance"],
                    "technologies": ["TaskUp"]
                },
                {
                    "text": "Compass Group implements security controls for all sectors using various technologies.",
                    "sectors": ["Healthcare", "Finance"],
                    "technologies": ["Security", "Compliance"]
                }
            ]
            
            # Create embeddings
            texts = [fact["text"] for fact in test_facts]
            embeddings = create_embeddings(texts)
            
            # Prepare points with metadata
            points = []
            for fact, embedding in zip(test_facts, embeddings):
                points.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "text": fact["text"],
                            "sectors": fact["sectors"],
                            "technologies": fact["technologies"]
                        }
                    )
                )
            
            # Upsert to Qdrant
            qdrant.upsert(
                collection_name=settings.qdrant_collection_name,
                points=points
            )
            
            print(f"✓ Inserted {len(points)} test facts with metadata")
            return True
            
        except Exception as e:
            print(f"⚠ Could not setup test data: {e}")
            return False

    def test_retrieval(
        self, 
        query: str, 
        sectors: Optional[List[str]] = None, 
        technologies: Optional[List[str]] = None,
        top_k: int = 5
    ):
        """
        Test retrieval with any query, sectors, and technologies.
        
        Args:
            query: Search query text
            sectors: Optional list of sectors to filter by
            technologies: Optional list of technologies to filter by
            top_k: Number of results to return (default: 5)
        """
        try:
            print("=" * 80)
            print(f"QUERY: {query}")
            if sectors:
                print(f"SECTORS FILTER: {sectors}")
            if technologies:
                print(f"TECHNOLOGIES FILTER: {technologies}")
            print("=" * 80)
            
            # Perform search
            results = search_qdrant(
                query=query,
                top_k=top_k,
                sectors=sectors,
                technologies=technologies
            )
            
            # Print results
            if not results:
                print(f"\n⚠ No results found for this query with the specified filters.")
            else:
                print(f"\n✓ Found {len(results)} result(s):\n")
                
                for i, result in enumerate(results, 1):
                    print(f"Result {i}:")
                    print(f"  Score: {result['score']:.4f}")
                    print(f"  Text: {result['text']}")
                    print(f"  Sectors: {result.get('sectors', [])}")
                    print(f"  Technologies: {result.get('technologies', [])}")
                    print()
            
            print("=" * 80)
            print()
            
            return results
            
        except Exception as e:
            print(f"❌ Error during retrieval: {e}")
            import traceback
            traceback.print_exc()
            return []


if __name__ == "__main__":
    print("=" * 80)
    print("Qdrant Retrieval Test with Filtering")
    print("=" * 80)
    print("\n⚠ Note: This test requires Qdrant to be running.")
    print("   Make sure Qdrant is accessible before running these tests.\n")
    
    # Create test instance
    test_instance = TestQdrantFiltering()
    
    # Optional: Setup test data if needed (uncomment if you want to insert test data)
    # print("Setting up test data...")
    # if not test_instance.setup_test_data():
    #     print("\n❌ Failed to setup test data. Exiting.")
    #     exit(1)
    # print()
    
    # Example test queries - modify these to test different queries
    print("Running example test queries...\n")
    
    # Example 1: Search without filters
    # test_instance.test_retrieval(
    #     query="list applications",
    #     top_k=5
    # )
    
    # # Example 2: Search with sector filter
    # test_instance.test_retrieval(
    #     query="list applications",
    #     sectors=["Healthcare"],
    #     top_k=5
    # )
    
    # # Example 3: Search with technology filter
    # test_instance.test_retrieval(
    #     query="list applications",
    #     technologies=["TaskUp"],
    #     top_k=5
    # )
    
    # # Example 4: Search with both filters
    # test_instance.test_retrieval(
    #     query="list applications",
    #     sectors=["Healthcare"],
    #     technologies=["TaskUp"],
    #     top_k=5
    # )
    
    # # Example 5: Search with multiple sectors and technologies
    test_instance.test_retrieval(
        query="List all the significant computer applications and the transaction class impacted?",
        sectors=["Bon Appetit"],
        technologies=["Agilysys"],
        top_k=10
    )
    
    print("\n" + "=" * 80)
    print("✓ Test completed!")
    print("=" * 80)
    print("\nTo test with your own queries, modify the test_retrieval() calls above")
    print("or call test_instance.test_retrieval(query, sectors, technologies) directly.")

