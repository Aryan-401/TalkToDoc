from agent_store import Agents
agent_class = Agents()


def test_audio_recognition():
    path = r"test/assets/audio.m4a"
    audio = open(path, "rb")
    assert agent_class.audio_to_text(audio) == " Hi there, how are you doing? I am doing pretty well."
    audio.close()
    print("Audio recognition test passed")
    return
