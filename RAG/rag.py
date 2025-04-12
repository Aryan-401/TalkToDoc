from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class Rag:
    def __init__(self, vector_store, embedder, history=None):
        if history is None:
            history = []
        self.prompt = hub.pull("rlm/rag-prompt")
        self.llm = init_chat_model(model_provider="groq", model="llama-3.3-70b-versatile")
        self.vector_store = vector_store
        self.embedder = embedder
        self.history = history
        self.prompt = self.get_prompt()
        self.threshold = 0.8

    def edit_threshold(self, threshold):
        self.threshold = threshold
        return 1

    def get_threshold(self):
        return self.threshold

    def get_prompt(self):
        prompt = ChatPromptTemplate([
            ("system", '''
                    You are an intelligent assistant that answers user questions based on both retrieved documents from a knowledge base and your own reasoning abilities.
                    When relevant documents are available, use them as the primary source of truth to generate accurate, grounded, and concise responses.
                    If the documents do not fully address the query or are unavailable, rely on your internal knowledge to generate a helpful and honest answer.
                    Do not fabricate references or hallucinate facts.
                    Always aim to be clear, helpful, and context-aware. If the user's question is ambiguous, ask clarifying questions before proceeding.
                    '''),
            ("ai", "The Documents from the knowledge base are: {context}"),
            MessagesPlaceholder(variable_name="history", optional=True),
            ("human", "{question}"),
        ])
        return prompt

    def generate_sources(self, documents, scores):
        src = []
        for document in documents:
            src.append({
                "source": document.metadata.get("source", ""),
                "type": document.metadata.get("type", ""),
                "file_id": document.metadata.get("file_id", ""),
                "chunk_id": document.metadata.get("chunk_id", ""),
                "score": scores[documents.index(document)],
            })
        return src

    def add_to_history(self, question, answer):
        self.history.extend(
            [
                {"role": "human", "content": question},
                {"role": "ai", "content": answer}
            ]
        )

    def retrieve_and_generate(self, question):
        retrieved_docs = self.vector_store.similarity_search_with_score(
            query=question,
            # embedding=self.embedder.get_query_jina_embeddings(question),
            k=5,
            score_threshold=self.threshold,
        )
        if retrieved_docs:
            retrieved_docs, scores = zip(*retrieved_docs)
            retrieved_docs = list(retrieved_docs)
            scores = list(scores)
        else:
            retrieved_docs = []
            scores = []

        sources= self.generate_sources(retrieved_docs, scores)
        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)
        prompt = self.prompt.invoke({"question": question, "context": docs_content, "history": self.history})
        answer = self.llm.invoke(prompt)
        self.add_to_history(question, answer.content)
        return answer.content, sources
