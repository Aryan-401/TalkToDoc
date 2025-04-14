import sys
import os
import time
import uuid
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter

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


# --- LangChain Text Splitter ---
def langchain_chunker(text, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,  # chunk size (characters)
        chunk_overlap=chunk_overlap,  # chunk overlap (characters)
        add_start_index=True,  # track index in original document
    )

    # Import Document class from langchain
    from langchain_core.documents import Document

    # Create a proper Document object
    docs = [Document(page_content=text, metadata={})]

    # Split the text using the splitter
    splits = text_splitter.split_documents(docs)

    # Extract just the text content from the splits
    chunks = [doc.page_content for doc in splits]
    start_indices = [doc.metadata.get("start_index", 0) for doc in splits]

    return chunks, start_indices


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
            # os.remove(filename)
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

    # Custom chunk size and overlap controls
    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.slider("Chunk Size (characters)", 500, 2000, 1000)
    with col2:
        chunk_overlap = st.slider("Chunk Overlap (characters)", 0, 500, 200)

    # Use the new langchain chunker
    chunks, start_indices = langchain_chunker(st.session_state.text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    st.write(f"🔍 Previewing {min(3, len(chunks))} of {len(chunks)} chunks:")
    for i, c in enumerate(chunks[:3]):
        st.code(f"[Chunk {i}, Start: {start_indices[i]}]\n{c[:400]}")

    if st.button("Add to Vector Database"):
        try:
            # Use the add method instead of add_embeddings_direct
            metadatas = [
                {
                    **st.session_state.metadata,
                    "chunk_id": i,
                    "data": chunk,
                    "file_id": file_id,
                    "start_index": start_indices[i]
                }
                for i, chunk in enumerate(chunks)
            ]
            st.code(metadatas[0])  # Show just first metadata record as example

            # Call the add method with chunks and metadata
            uuids = qdrant_link.add(documents=chunks, metadata=metadatas)

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
                for file in os.listdir(r"qdrant_docustore/files"):
                    os.remove(os.path.join(r"qdrant_docustore/files", file))
                st.success("✅ Vector DB has been cleared.")
            except Exception as e:
                st.error(f"Error clearing vector DB: {e}")