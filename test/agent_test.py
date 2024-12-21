#! pytest .\test\agent_test.py
import json
from models import History
from agent_store import Agents
from test import helper
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

def test_supervisor_and_general_manager_whole():
    history = [
        History(speaker="user", message="Hello"),
        History(speaker="assistant", message="Hi")
    ]
    ideal_answer = """{
    "type": "everyday",
    "response": "Hi! How can I help?"
    }"""

    score = helper.test_supervisor_and_general_manager(agent_class, ideal_answer, history, "Hello")
    assert score >= 0.7
    ideal_answer = """{
    "type": "domain",
    "response": '["Q3_financial_report.pdf", "profit_analysis.xlsx"]'
    }"""
    score = helper.test_supervisor_and_general_manager(agent_class, ideal_answer, history, "How do thr profits in Q3 look?")
    assert score >= 0.7
