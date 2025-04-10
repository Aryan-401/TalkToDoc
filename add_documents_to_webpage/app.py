import sys
import os
import time
import uuid
from datetime import datetime

import nltk
from nltk.tokenize import sent_tokenize

# Download both punkt and punkt_tab
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# Specifically add punkt_tab download
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

from dotenv import load_dotenv

load_dotenv()

import streamlit as st

st.set_page_config(page_title="Vector DB Uploader", layout="centered")

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from qdrant_docustore import JinaEmbed
from qdrant_docustore import QdrantLink
from file_to_text import ConvertDocument


# Session setup
@st.cache_resource
def get_session():
    qdrant_link_local = QdrantLink()
    jina_embed_local = JinaEmbed()
    print(datetime.now())
    return qdrant_link_local, jina_embed_local


qdrant_link, jina_embed = get_session()


# --- Sentence-aware Chunker ---
def sentence_chunker(text, max_tokens=200):
    from transformers import GPT2TokenizerFast
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

    # Modified error handling for punkt_tab
    try:
        sentences = sent_tokenize(text)
    except LookupError as e:
        st.error(f"NLTK tokenizer error: {str(e)}")
        # Try to fix the issue by downloading punkt directly
        nltk.download("punkt")

        # If punkt_tab is specifically needed, download it too
        try:
            nltk.download("punkt_tab")
        except:
            pass

        # Try again
        try:
            sentences = sent_tokenize(text)
        except Exception as new_e:
            # If still failing, fall back to a simple splitter
            st.warning("Using fallback sentence splitter")
            sentences = [s.strip() + "." for s in text.split(".") if s.strip()]

    chunks = []
    current_chunk = []

    for sentence in sentences:
        tokens = tokenizer.encode(" ".join(current_chunk + [sentence]))
        if len(tokens) <= max_tokens:
            current_chunk.append(sentence)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# --- Streamlit UI ---

st.title("📚 Add Documents to Vector Database")
st.write("Upload a document or input text to convert and store in the vector DB as searchable chunks.")

converter = ConvertDocument()
st.tabs = st.selectbox("Select the type of document", ["Webpage", "File (we'll try our best)", "Text"])
text = None
metadata = None

if st.tabs == "Webpage":
    url = st.text_input("Enter the URL of the webpage")
    if st.button("Convert Webpage to Text"):
        if url:
            text = converter.convert_webpage_to_text(url)
            metadata = {"source": url, "type": "webpage"}
            st.session_state.text = text
            st.session_state.metadata = metadata
            st.success("Webpage converted successfully!")
        else:
            st.error("Please enter a valid URL.")

elif st.tabs == "File (we'll try our best)":
    file = st.file_uploader("Upload a file", type=["txt", "pdf", "docx", "jpg", "png"])
    if st.button("Convert File to Text"):
        if file:
            filename = "qdrant_docustore/files/" + file.name
            with open(filename, "wb") as f:
                f.write(file.getbuffer())
            text = converter.convert_files_to_text(filename)
            os.remove(filename)
            metadata = {"source": filename, "type": "file"}
            st.session_state.text = text
            st.session_state.metadata = metadata
            st.success("File converted successfully!")
        else:
            st.error("Please upload a valid file.")

elif st.tabs == "Text":
    input_text = st.text_area("Enter the text")
    if st.button("Commit to this text"):
        if input_text.strip():
            st.session_state.text = input_text
            st.session_state.metadata = {"source": "user_input", "type": "text"}
            st.success("Text committed successfully!")
        else:
            st.error("Please enter some text.")

# --- Show chunk preview and add to DB ---
if "text" in st.session_state and "metadata" in st.session_state:
    st.divider()
    st.write("✅ Text committed. Document will be chunked for embedding.")
    # get sha256 hash of the text
    file_id = uuid.uuid4()
    chunks = sentence_chunker(st.session_state.text, max_tokens=200)
    st.write(f"🔍 Previewing {min(3, len(chunks))} of {len(chunks)} chunks:")
    for i, c in enumerate(chunks[:3]):
        st.code(f"[Chunk {i}]\n{c[:400]}")

    if st.button("Add to Vector Database"):
        try:
            embeddings = jina_embed.get_document_jina_embeddings(chunks)
            metadatas = [
                {**st.session_state.metadata, "chunk_id": i, "data": chunk, "file_id": file_id}
                for i, chunk in enumerate(chunks)
            ]
            st.code(metadatas)
            uuids = []
            for n in range(len(embeddings)):
                uuids.append(qdrant_link.add_embeddings_direct(embedding=embeddings[n],
                                                  metadata=metadatas[n]))
            st.success(f"✅ {len(uuids)} chunks added to vector database.")
            del st.session_state.text
            del st.session_state.metadata
        except Exception as e:
            st.error(f"Error adding to vector DB: {e}")

# --- Show all documents ---
if st.button("Show All Documents (Last 1k)"):
    try:
        all_documents = qdrant_link.show_all_documents()
        for doc in all_documents:
            st.code(doc.model_dump_json())
    except Exception as e:
        st.error(f"Error fetching documents: {e}")

# --- Delete vector DB ---
st.divider()
with st.expander("⚠️ Dangerous: Delete Entire Vector DB"):
    if st.checkbox("I understand that this cannot be undone"):
        if st.button("Delete All Data from Vector DB"):
            try:
                qdrant_link.clear_collection()
                st.success("✅ Vector DB has been cleared.")
            except Exception as e:
                st.error(f"Error clearing vector DB: {e}")