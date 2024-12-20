#! pytest .\test\agent_test.py
import json

from agent_store import Agents

agent_class = Agents()


def test_audio_recognition():
    path = r"test/assets/audio.m4a"
    audio = open(path, "rb")
    score = agent_class.testing__evaluation_judge(agent_class.audio_to_text(audio),
                                                  "Hi there, how are you doing? I am doing pretty well.")
    print("In Audio Recognition, the score is: ", score)
    assert score >= 0.7
    audio.close()
    return

def test_supervisor_and_general_manager():
    history = [
        {
            "sender": "user",
            "message": "Hello"
        },
        {
            "sender": "assistant",
            "message": "Hi"
        }
    ]
    ideal_answer = """{
"type": "everyday",
"response": "Hi! How can I help?"
}"""
    response = agent_class.supervisor_and_general_manager("Hello", history)
    try:
        response_dict = json.loads(response)
        type_, response_ = response_dict["type"], response_dict["response"]
    except:
        raise AssertionError("The response is not in JSON/Proper JSON format")
    print("In Supervisor and General Manager, the response is: ", response)
    score = agent_class.testing__evaluation_judge(response, ideal_answer)
    assert score >= 0.7
    return