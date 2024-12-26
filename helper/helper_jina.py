import requests
from typing import List, Dict
import os


def helper__web_to_markdown(website: str) -> str:
    headers = {
        'Authorization': 'Bearer ' + os.environ.get("JINA_API_KEY")
    }
    base_jina = "https://r.jina.ai/"
    url = base_jina + website
    response = requests.get(url,
                            # headers=headers
                            )
    return response.text


def helper__multimodal_embeddings(content: List[Dict[str, str]]):
    import requests

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.environ.get("JINA_API_KEY")
    }

    data = {
        "model": "jina-clip-v2",
        "dimensions": 1,
        "normalized": True,
        "embedding_type": "float",
        "input": content
    }

    response = requests.post("https://api.jina.ai/v1/embeddings",
                             headers=headers,
                             json=data
                             )
    print(response.json())
    return response.json()
