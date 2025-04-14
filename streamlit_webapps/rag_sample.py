import streamlit as st
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RAG import Rag
from qdrant_docustore import QdrantLink, JinaEmbed

st.set_page_config(
    page_title="RAG Chat Assistant",
    page_icon="💬",
    layout="wide"
)

# Add some custom CSS for source citations and other styling
st.markdown("""
<style>
    .source-citation {
        font-size: 0.85em;
        color: #505050;
        padding-top: 0.5rem;
        border-top: 1px solid #e6e6e6;
        margin-top: 0.5rem;
    }
    .source-item {
        margin-bottom: 0.3rem;
        padding-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.title("RAG Chat Assistant")
st.markdown("Ask questions and get answers powered by LLaMA 3.3 70B with document retrieval.")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'rag_system' not in st.session_state:
    with st.spinner("Initializing RAG system..."):
        try:
            f = QdrantLink()
            g = JinaEmbed()
            st.session_state.rag_system = Rag(qdlink=f, embedder=g)
            st.success("RAG system initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing RAG system: {str(e)}")
            st.stop()


# Function to format source display
def format_sources(sources):
    if not sources:
        return ""
    formatted = "<div class='source-citation'><strong>Sources:</strong>"
    for src in sources:
        source_text = []
        if src.get("source"):
            source_val = src["source"]
            if source_val.startswith("http://") or source_val.startswith("https://"):
                display_text = source_val[:50] + ("..." if len(source_val) > 50 else "")
                source_text.append(f'Source: <a href="{source_val}" target="_blank">{display_text}</a>')
            else:
                source_text.append(f"Source: {source_val}")
        if src.get("file_id"):
            source_text.append(f"File ID: {src['file_id']}")
        if src.get("chunk_id"):
            source_text.append(f"Chunk ID: {src['chunk_id']}")
        if src.get("score"):
            source_text.append(f"Score: {src['score']:.3f}")
        if src.get("reranked_score"):
            source_text.append(f"Reranked Score: {src['reranked_score']:.3f}")
        formatted += f"<div class='source-item'>{', '.join(source_text)}</div>"
    formatted += "</div>"
    return formatted


# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            st.markdown(message["sources"], unsafe_allow_html=True)

# React to user input
if prompt := st.chat_input("Ask a question about your documents..."):
    st.chat_message("human").markdown(prompt)
    st.session_state.messages.append({"role": "human", "content": prompt})

    with st.spinner("Searching documents and generating response..."):
        try:
            answer, sources = st.session_state.rag_system.retrieve_and_generate(prompt)
            formatted_sources = format_sources(sources)
        except Exception as e:
            answer = f"Error generating response: {str(e)}"
            formatted_sources = ""

    with st.chat_message("ai"):
        st.markdown(answer)
        if formatted_sources:
            st.markdown(formatted_sources, unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "ai",
        "content": answer,
        "sources": formatted_sources
    })

# Sidebar components
with st.sidebar:
    st.title("Settings")

    st.info("Using LLaMA 3.3 70B Versatile model via Groq")

    if 'rag_system' in st.session_state:
        pre_rank_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.rag_system.pre_rank_threshold,
            step=0.05,
            help="Minimum similarity score required for document retrieval"
        )
        if pre_rank_threshold != st.session_state.rag_system.get_pre_threshold():
            st.session_state.rag_system.edit_pre_threshold(pre_rank_threshold)
            st.success(f"Pre Ranking Threshold updated to {pre_rank_threshold}")

        post_rank_threshold = st.slider(
            "Post Ranking Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.rag_system.post_rank_threshold,
            step=0.05,
            help="Minimum similarity score required for document retrieval after Reranking"
        )
        if post_rank_threshold != st.session_state.rag_system.get_post_threshold():
            st.session_state.rag_system.edit_post_threshold(pre_rank_threshold)
            st.success(f"Post Ranking Threshold updated to {pre_rank_threshold}")


    if st.button("Clear Chat History", key="clear_chat"):
        st.session_state.messages = []
        if 'rag_system' in st.session_state:
            st.session_state.rag_system.history = []
        st.success("Chat history cleared!")
        st.rerun()

    st.title("About")
    st.markdown("""
    This chat application uses a Retrieval-Augmented Generation (RAG) system to answer your questions.

    The system:
    1. Takes your question
    2. Embeds it using Jina embeddings
    3. Retrieves relevant documents from Qdrant vector database
    4. Uses LLaMA 3.3 70B to generate an answer based on the retrieved documents
    5. Shows you the source information for context

    Try asking questions related to the content in your document collection!
    """)
