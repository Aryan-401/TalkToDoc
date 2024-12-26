import requests


def helper__web_to_markdown(website: str) -> str:
    headers = {
        'Authorization': 'Bearer' +
    }
    base_jina = "https://r.jina.ai/"
    url = base_jina + website
    response = requests.get(url, headers=headers)
    return response
