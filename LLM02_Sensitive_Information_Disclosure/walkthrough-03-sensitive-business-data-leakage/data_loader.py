from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"

CLASSIFICATION_MAP = {
    "public": "public",
    "internal": "internal",
    "confidential": "confidential",
}


def load_documents():
    documents = []

    for folder_name, classification in CLASSIFICATION_MAP.items():
        folder_path = DATA_DIR / folder_name

        if not folder_path.exists():
            continue

        for file_path in sorted(folder_path.glob("*.txt")):
            text = file_path.read_text(encoding="utf-8").strip()

            if not text:
                continue

            documents.append({
                "text": text,
                "source": file_path.name,
                "classification": classification,
            })

    return documents


def chunk_text(text, chunk_size=500, overlap=100):
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def load_and_chunk_documents(chunk_size=500, overlap=100):
    documents = load_documents()
    chunks = []

    for document in documents:
        document_chunks = chunk_text(
            document["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for index, chunk in enumerate(document_chunks):
            chunks.append({
                "text": chunk,
                "source": document["source"],
                "classification": document["classification"],
                "chunk_id": index,
            })

    return chunks