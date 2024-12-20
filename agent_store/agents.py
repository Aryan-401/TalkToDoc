from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class Agents():
    def __init__(self):
        self.audio_model = Groq()
        self.text_model = ChatGroq()

    def audio_to_text(self, audio, model="whisper-large-v3-turbo", language="en"):
        return self.audio_model.audio.transcriptions.create(model=model, file=audio, language=language, response_format="text")
