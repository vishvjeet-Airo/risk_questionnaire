from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid
from app.core.config import settings
from app.core.clients.bedrock import bedrock_client


COLLECTION_NAME = settings.qdrant_collection_name
VECTOR_DIM = settings.vector_dim

# Qdrant client 
qdrant = QdrantClient(
    host=settings.qdrant_host, 
    port=settings.qdrant_port
)


def ensure_collection():
    """Create Qdrant collection if it doesn’t exist."""
    if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
        )

# Chunking strategy - consider one paragraph as a chunk considering the 
# paragraphs are itself independent and contains enough context 
def paragraph_chunks(text: str) -> list[str]:
    """
    Split story text into paragraphs.
    Paragraphs are separated by two newlines.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs


def create_embeddings(chunks: list[str]) -> list[list[float]]:
    """Generate embeddings from Azure OpenAI."""
    response = bedrock_client.embed_texts(chunks)
    return response


def store_in_qdrant(chunks: list[str], embeddings: list[list[float]]):
    """Store text chunks with embeddings in Qdrant."""
    points = []
    for chunk, embedding in zip(chunks, embeddings):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"text": chunk}
            )
        )
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"✅ Stored {len(points)} paragraphs in Qdrant collection '{COLLECTION_NAME}'")

def embed_text(text: str) -> list[float]:
    emb = bedrock_client.embed_text(text)
    return emb

def search_qdrant(query: str, top_k=5):
    vector = embed_text(query)
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=top_k,
    )
    return [
        {
            "text": hit.payload.get("text", ""),
            "score": hit.score
        }
        for hit in results
    ]

def process_story_to_qdrant(story_text: str):
    ensure_collection()
    chunks = paragraph_chunks(story_text)
    embeddings = create_embeddings(chunks)
    store_in_qdrant(chunks, embeddings)

if __name__ == "__main__":
    with open("story_output_batched.txt", "r", encoding="utf-8") as f:
        story_text = f.read()
    process_story_to_qdrant(story_text)
