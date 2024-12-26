from typing import List, Tuple
from models import History


def helper_history__history_to_chat_prompt(history: List[History], messages: List[Tuple[str, str]], query: str):
    for message in history:
        messages.append((message.speaker.value, message.message))

    messages.append(("user", query))
    return messages
