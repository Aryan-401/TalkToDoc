def helper_history__history_to_chat_prompt(history, messages, query):
    for message in history:
        if message["sender"] == "user":
            messages.append(("user", message["message"]))
        else:
            messages.append(("assistant", message["message"]))

    messages.append(("user", query))
    return messages
