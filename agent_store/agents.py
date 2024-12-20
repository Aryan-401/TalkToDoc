from langchain_core.prompts import ChatPromptTemplate
import os
from models import History
from langchain_groq import ChatGroq
from groq import Groq
from dotenv import load_dotenv
from agent_store.helper_history import helper_history__history_to_chat_prompt

load_dotenv()


class Agents:
    def __init__(self):
        self.audio_model = Groq()
        self.text_model = ChatGroq(model="llama-3.3-70b-versatile")  # or llama-3.3-70b-specdec
        self.system_prompts = {}
        for file in os.listdir("agent_store/assets"):
            if file.endswith(".md"):
                self.system_prompts[file[:-3]] = open(f"agent_store/assets/{file}", "r").read()

    def audio_to_text(self, audio, model="whisper-large-v3-turbo", language="en"):
        return self.audio_model.audio.transcriptions.create(model=model, file=audio, language=language,
                                                            response_format="text")

    def supervisor_and_general_manager(self, query, history: History):
        messages = [("system", self.system_prompts[self.supervisor_and_general_manager.__name__])]
        helper_history__history_to_chat_prompt(history, messages, query)
        template = ChatPromptTemplate(messages)
        answer = template | self.text_model
        return answer.invoke(input={"query": query}).content

