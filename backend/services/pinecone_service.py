from pinecone import Pinecone
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from services.embedding_service import create_embedding
import uuid


# Connect to Pinecone (yeh index variable banata hai)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)


def search_pinecone(embedding, top_k=5):
    results = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True
    )
    return [match["metadata"]["text"] for match in results["matches"]]


def split_text(text, chunk_size=500):
    words = text.split()
    return [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]


def upsert_document(text, source):
    chunks = split_text(text)
    vectors = []

    for chunk in chunks:
        embedding = create_embedding(chunk)
        vectors.append({
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {
                "text": chunk,
                "source": source
            }
        })

    if vectors:
        index.upsert(vectors=vectors)

    return len(vectors)