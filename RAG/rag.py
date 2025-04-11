from langchain import hub
from langchain.chat_models import init_chat_model


class Rag:
    def __init__(self, vector_store):
        self.prompt = hub.pull("rlm/rag-prompt")
        self.llm = init_chat_model(model_provider="groq", model="llama-3.3-70b-versatile")
        self.vector_store = vector_store

    def retrieve_and_generate(self, question):
        prompt = hub.pull("rlm/rag-prompt")

        retrieved_docs = self.vector_store.similarity_search(question)
        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)
        prompt = prompt.invoke({"question": question, "context": docs_content})
        answer = self.llm.invoke(prompt)
        return answer.content
