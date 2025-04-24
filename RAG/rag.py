from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from agent_store.agents import Agents

class Rag:
    def __init__(self, qdlink, embedder, history=None):
        if history is None:
            history = []
        self.llm = init_chat_model(model_provider="groq", model="llama-3.3-70b-versatile")
        self.qdlink = qdlink
        self.embedder = embedder
        self.history = history
        self.prompt = self.get_prompt()
        self.pre_rank_threshold = 0.5
        self.post_rank_threshold = 0.1
        self.agents = Agents()

    def get_pre_threshold(self):
        return self.pre_rank_threshold

    def get_post_threshold(self):
        return self.post_rank_threshold

    def edit_pre_threshold(self, new_threshold):
        self.pre_rank_threshold = new_threshold
        return self.pre_rank_threshold

    def edit_post_threshold(self, new_threshold):
        self.post_rank_threshold = new_threshold
        return self.post_rank_threshold

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
                "reranked_score": document.metadata.get("reranked_score", ""),
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
        # metadata_topics = self.agents.create_metadata(question)
        retrieved_docs = self.qdlink.query_and_rerank(query=question, pre_rank_threshold=self.pre_rank_threshold, post_rank_threshold=self.post_rank_threshold,
                                                      # metadata_filter=metadata_topics
                                                      )
        if retrieved_docs:
            retrieved_docs, scores = zip(*retrieved_docs)
            retrieved_docs = list(retrieved_docs)
            scores = list(scores)
        else:
            retrieved_docs = []
            scores = []

        sources = self.generate_sources(retrieved_docs, scores)
        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)
        prompt = self.prompt.invoke({"question": question, "context": docs_content, "history": self.history})
        answer = self.llm.invoke(prompt)
        self.add_to_history(question, answer.content)
        return answer.content, sources
