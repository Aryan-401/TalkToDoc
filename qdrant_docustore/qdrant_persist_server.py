import json
from uuid import uuid4
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, FilterSelector, Filter
from qdrant_docustore import embeddings
from typing import List, Dict


class QdrantLink:
    def __init__(self):
        self.client = QdrantClient(path="qdrant_docustore/qdrant_store")
        self.embeddings = embeddings.JinaEmbed().text_embeddings
        all_collections = [a.get("name", None) for a in
                           json.loads(self.client.get_collections().model_dump_json())['collections']]
        if 'docustore' not in all_collections:
            self.client.create_collection(collection_name="docustore",
                                          vectors_config=VectorParams(
                                              size=1024,
                                              distance=Distance.COSINE,
                                          )
                                          )
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name="docustore",
            embedding=self.embeddings
        )

    def add(self, documents: List[str], metadata: List[Dict[str, str]]):
        generated_uuids = [str(uuid4()) for _ in range(len(documents))]
        final_documents = []
        for index in range(len(documents)):
            final_documents.append(
                Document(
                    page_content=documents[index],
                    metadata=metadata[index]
                )
            )
        self.vector_store.add_documents(documents=final_documents, ids=generated_uuids)
        return generated_uuids

    def delete(self, uuid: List[str]):
        if uuid is None:
            raise ValueError("UUID cannot be None for deletion.")
        self.vector_store.delete(ids=uuid)
        return uuid

    def close_connection(self):
        self.client.close()
        return True

    def clear_collection(self):
        self.client.delete(collection_name="docustore", points_selector=FilterSelector(
            filter=Filter(
                must=[]
            )
        )
                           )
        return True
