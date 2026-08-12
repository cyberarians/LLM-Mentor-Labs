import json
from pathlib import Path

import faiss
from dotenv import load_dotenv

from data_loader import load_and_chunk_documents
from embeddings import generate_embeddings


load_dotenv()


VECTORSTORE_DIR = Path(__file__).parent / "vectorstore"


ROLE_ACCESS = {
    "employee": {
        "public",
    },
    "manager": {
        "public",
        "internal",
    },
    "executive": {
        "public",
        "internal",
        "confidential",
    },
}


class BusinessDataRetriever:

    def __init__(self):
        self.documents = load_and_chunk_documents()

        self.indexes = {}
        self.metadata = {}

        VECTORSTORE_DIR.mkdir(
            exist_ok=True
        )

        self._build_indexes()

    # =========================================================
    # Build / Load Vector Stores
    # =========================================================

    def _build_indexes(self):

        grouped_documents = {}

        for document in self.documents:

            classification = document[
                "classification"
            ]

            if classification not in grouped_documents:

                grouped_documents[
                    classification
                ] = []

            grouped_documents[
                classification
            ].append(document)

        for (
            classification,
            documents,
        ) in grouped_documents.items():

            index_path = (
                VECTORSTORE_DIR
                / f"{classification}.faiss"
            )

            metadata_path = (
                VECTORSTORE_DIR
                / f"{classification}.json"
            )

            index = None
            metadata = None

            # -------------------------------------------------
            # Load existing vector store
            # -------------------------------------------------

            if (
                index_path.exists()
                and metadata_path.exists()
            ):

                try:

                    index = faiss.read_index(
                        str(index_path)
                    )

                    with open(
                        metadata_path,
                        "r",
                        encoding="utf-8",
                    ) as file:

                        metadata = json.load(
                            file
                        )

                    # Rebuild if document count changed
                    if len(metadata) != len(
                        documents
                    ):

                        index = None
                        metadata = None

                except Exception:

                    index = None
                    metadata = None

            # -------------------------------------------------
            # Build vector store
            # -------------------------------------------------

            if (
                index is None
                or metadata is None
            ):

                texts = [
                    document["text"]
                    for document in documents
                ]

                vectors = generate_embeddings(
                    texts
                )

                if vectors.size == 0:
                    continue

                dimension = vectors.shape[1]

                index = faiss.IndexFlatL2(
                    dimension
                )

                index.add(
                    vectors
                )

                metadata = documents

                faiss.write_index(
                    index,
                    str(index_path)
                )

                with open(
                    metadata_path,
                    "w",
                    encoding="utf-8",
                ) as file:

                    json.dump(
                        metadata,
                        file,
                        indent=2,
                    )

            self.indexes[
                classification
            ] = index

            self.metadata[
                classification
            ] = metadata

    # =========================================================
    # Get Allowed Classifications
    # =========================================================

    def get_allowed_classifications(
        self,
        user_role,
        mode,
    ):

        if mode.lower() == "vulnerable":

            return list(
                self.metadata.keys()
            )

        return list(
            ROLE_ACCESS.get(
                user_role,
                {"public"},
            )
        )

    # =========================================================
    # Retrieve Business Information
    # =========================================================

    def search(
        self,
        query,
        user_role="employee",
        mode="vulnerable",
    ):

        allowed_classifications = (
            self.get_allowed_classifications(
                user_role,
                mode,
            )
        )

        results = []

        # -----------------------------------------------------
        # IMPORTANT:
        #
        # No top_k
        # No semantic ranking
        # No similarity filtering
        #
        # Every chunk inside the authorized scope
        # is returned.
        # -----------------------------------------------------

        for classification in (
            allowed_classifications
        ):

            documents = self.metadata.get(
                classification,
                [],
            )

            for document in documents:

                results.append(
                    {
                        "text": document[
                            "text"
                        ],

                        "source": document[
                            "source"
                        ],

                        "classification": document[
                            "classification"
                        ],

                        "chunk_id": document[
                            "chunk_id"
                        ],
                    }
                )

        return results


def get_retriever():

    return BusinessDataRetriever()