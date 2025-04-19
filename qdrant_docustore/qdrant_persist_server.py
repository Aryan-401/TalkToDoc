import json
from uuid import uuid4
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain_community.document_compressors import JinaRerank
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, FilterSelector, Filter, FieldCondition, MatchAny
from qdrant_docustore import embeddings
from typing import List, Dict
from pprint import pprint


class QdrantLink:
    def __init__(self, location="qdrant_docustore/qdrant_store", collection_name="docustore"):
        self.client = QdrantClient(path=location)
        self.embeddings = embeddings.JinaEmbed().text_embeddings
        all_collections = [a.get("name", None) for a in
                           json.loads(self.client.get_collections().model_dump_json())['collections']]
        if collection_name not in all_collections:
            self.client.create_collection(collection_name="docustore",
                                          vectors_config=VectorParams(
                                              size=1024,
                                              distance=Distance.COSINE,
                                          )
                                          )
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name="docustore",
            embedding=self.embeddings,
            retrieval_mode=RetrievalMode.DENSE
        )

    def return_client(self):
        return self.client

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

    def add_embeddings_direct(self, embedding, metadata):
        generated_uuid = str(uuid4())
        self.vector_store.add_documents(documents=[
            Document(
                embedding=embedding,
                page_content="",
                metadata=metadata
            )
        ],
            ids=[generated_uuid], )
        return generated_uuid

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

    def query_collection(self, query: str, k: int = 5, threshold: float = 0.5, metadata_filter: dict = None):
        if metadata_filter is None:
            metadata_filter = {}
        if not isinstance(metadata_filter, dict):
            raise TypeError("metadata_filter must be a dictionary")
        print(metadata_filter)
        filter_any = Filter(
            should=[
                FieldCondition(
                    key="topics",
                    match=MatchAny(
                        any=metadata_filter.get("topic", [])
                    )
                )
            ]
        )
        print(filter_any)
        result = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            score_threshold=threshold,
            # filter=filter_any
        )
        return result

    def show_all_documents(self):
        result = self.vector_store.similarity_search(query="", score_threshold=-1, k=1000)
        return result

    def query_and_rerank(self, query: str, k_pre_rank: int = 20, k_post_rank: int = 7, pre_rank_threshold: float = 0.5,
                         post_rank_threshold: float = 0.7, metadata_filter: dict = None):
        doc_and_score = self.query_collection(query=query, k=k_pre_rank, threshold=pre_rank_threshold, metadata_filter=metadata_filter)

        if not doc_and_score:
            return []
        doc, score = zip(*doc_and_score)
        jina = JinaRerank()
        reranked_results = jina.rerank(
            documents=list(doc),
            query=query,
            top_n=k_post_rank,
        )
        final_return = []
        for col in reranked_results:
            if col["relevance_score"] >= post_rank_threshold:
                doc_and_score[col['index']][0].metadata['reranked_score'] = col['relevance_score']
                final_return.append(doc_and_score[col['index']])

        return final_return
