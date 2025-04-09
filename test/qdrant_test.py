#! pytest .\test\qdrant_test.py
from qdrant_docustore import JinaEmbed
from qdrant_docustore import QdrantLink


def test_jina_embed_query():
    j = JinaEmbed()
    query = "Hello, how are you doing?"
    result = j.get_query_jina_embeddings(query)
    assert isinstance(result, list)
    assert len(result) == 1024


def test_jina_embed_document():
    j = JinaEmbed()
    document = ["Hello, how are you doing?", "I am doing well"]
    result = j.get_document_jina_embeddings(document)
    assert isinstance(result, list)
    assert len(result) == 2
    assert len(result[0]) == 1024
    assert len(result[1]) == 1024


def test_qdrant_add(link: QdrantLink):
    documents = ["Hello, how are you doing?", "I am doing well"]
    metadata = [{"name": "John Doe"}, {"name": "Jane Doe"}]
    uuid = link.add(documents, metadata)
    assert isinstance(uuid, list)
    link.close_connection()
    assert len(uuid) == 2


def test_qdrant_delete(link: QdrantLink):
    documents = ["Hello, how are you doing?", "I am doing well"]
    metadata = [{"name": "John Doe"}, {"name": "Jane Doe"}]
    uuid = link.add(documents, metadata)
    assert isinstance(uuid, list)
    assert len(uuid) == 2
    assert link.delete(uuid) == uuid
    link.close_connection()


def test_qdrant_query(link: QdrantLink):
    documents = ["Hello, how are you doing?", "I am doing well"]
    metadata = [{"name": "John Doe"}, {"name": "Jane Doe"}]
    uuid = link.add(documents, metadata)
    assert isinstance(uuid, list)
    assert len(uuid) == 2
    result = link.query_collection("Hello, how are you doing?")
    for res in result:
        print(res.model_dump_json())
    link.close_connection()


def test_qdrant_clean(link: QdrantLink):
    link.clear_collection()
    link.close_connection()
