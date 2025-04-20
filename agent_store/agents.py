from typing import List

from langchain_core.prompts import ChatPromptTemplate
import os
from models import History
from langchain_groq import ChatGroq
from groq import Groq
from dotenv import load_dotenv
from helper import helper_history__history_to_chat_prompt
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

load_dotenv()


class Agents:
    def __init__(self):
        self.audio_model = Groq()
        self.text_model = ChatGroq(model="llama-3.3-70b-versatile")  # or llama-3.3-70b-specdec
        self.judging_model = ChatGroq(model="gemma2-9b-it")
        self.metadata_model = init_chat_model("llama3-8b-8192", model_provider="groq")
        self.system_prompts = {}
        for file in os.listdir("agent_store/assets"):
            with open("agent_store/assets/" + file, "r") as f:
                if file.endswith(".md"):
                    self.system_prompts[file[:-3]] = f.read()

    def audio_to_text(self, audio, model="whisper-large-v3-turbo", language="en"):
        return self.audio_model.audio.transcriptions.create(model=model, file=audio, language=language,
                                                            response_format="text")

    def supervisor_and_general_manager(self, query, history: List[History]):
        messages = [("system", self.system_prompts[self.supervisor_and_general_manager.__name__])]
        helper_history__history_to_chat_prompt(history, messages, query)
        template = ChatPromptTemplate(messages)
        answer = template | self.text_model
        return answer.invoke(input={"query": query}).content

    def testing__evaluation_judge(self, response, ideal_answer):
        messages = [("system", self.system_prompts[self.testing__evaluation_judge.__name__])]
        template = ChatPromptTemplate(messages)
        answer = template | self.judging_model
        try:
            score = float(answer.invoke(input={"response": response, "ideal_response": ideal_answer}).content)
        except Exception as e:
            print(f"Exception: {e}")
            score = -1.0
        return score

    def create_metadata(self, query):
        class Metadata(BaseModel):
            topic: List[Optional[str]] = Field(default_factory=list,
                                               description="General topics of the document as a list of strings.")

        struct_llm = self.metadata_model.with_structured_output(Metadata)
        ans = struct_llm.invoke(query)
        return ans.model_dump()
