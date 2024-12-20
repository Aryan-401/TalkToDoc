#! pytest .\test\agent_test.py

from agent_store import Agents
agent_class = Agents()



def test_audio_recognition():
    path = r"test/assets/audio.m4a"
    audio = open(path, "rb")
    assert agent_class.testing__evaluation_judge(agent_class.audio_to_text(audio), "Hi there, how are you doing? I am doing pretty well.") >= 0.7
    audio.close()
    return
