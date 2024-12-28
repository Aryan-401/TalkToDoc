from typing import List
from langchain_community.embeddings import JinaEmbeddings


class JinaEmbed:
    def __init__(self):
        self.text_embeddings = JinaEmbeddings(
            model_name="jina-embeddings-v3",
            model_config={
                "task": "retrieval.passage",
                "late_chunking": True,
                "dimensions": "1024",
                "embedding_type": "float",
            }
        )

    def get_query_jina_embeddings(self, query: str):
        query_result = self.text_embeddings.embed_query(query)
        return query_result

    def get_document_jina_embeddings(self, text_list: List[str]):
        document_result = self.text_embeddings.embed_documents(text_list)
        return document_result

    
