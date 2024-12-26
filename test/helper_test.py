#! pytest .\test\helper_test.py
import helper
from models import History


def test_history_to_chat_prompt():
    history = [
        History(speaker="user", message="Hello"),
        History(speaker="assistant", message="Hi"),
        History(speaker="user", message="How are you"),
        History(speaker="assistant", message="I am well")
    ]
    messages = []
    query = "What is your name?"
    answer = helper.helper_history.helper_history__history_to_chat_prompt(history, messages, query)
    assert answer == [
        ("user", "Hello"),
        ("assistant", "Hi"),
        ("user", "How are you"),
        ("assistant", "I am well"),
        ("user", "What is your name?")
    ]


def test_jina_website_to_markdown():
    website = "https://thapar.edu"
    markdown = helper.helper_jina.helper__web_to_markdown(website)
    assert isinstance(markdown, str)
    assert len(markdown) > 0


def test_jina_multimodal_embeddings():
    content = [
        {"text": "Hello, how are you doing?"},
        # {
        #     "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Picture_of_a_Dog%2C_%22Doggo%22%2C_%22Pupper%22.jpg/1200px-Picture_of_a_Dog%2C_%22Doggo%22%2C_%22Pupper%22.jpg"
        # },
    ]
    embeddings = helper.helper_jina.helper__multimodal_embeddings(content)
    testable = embeddings.get("data", [None])
    for test in testable:
        assert isinstance(test.get("embedding", None), list)


def test_jina_text_embeddings():
    content = ["Hello, how are you doing?", "I am doing well"]
    embeddings = helper.helper_jina.helper__text_embeddings(content)
    testable = embeddings.get("data", [None])
    for test in testable:
        assert isinstance(test.get("embedding", None), list)
        assert len(test.get("embedding", [])) == 1024
