import os
import uuid

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

from config import PINECONE_API_KEY, PINECONE_INDEX_NAME


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Connect to Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)


def split_text(text, chunk_size=500):
    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def ingest_documents():
    documents_folder = "data/documents"

    for filename in os.listdir(documents_folder):

        file_path = os.path.join(documents_folder, filename)

        if not os.path.isfile(file_path):
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        chunks = split_text(text)

        vectors = []

        for chunk in chunks:

            embedding = model.encode(chunk).tolist()

            vector_id = str(uuid.uuid4())

            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "source": filename
                }
            })

        if vectors:
            index.upsert(vectors=vectors)

        print(f"Uploaded {filename}: {len(vectors)} chunks")


if __name__ == "__main__":
    ingest_documents()
    print("Document ingestion completed.")