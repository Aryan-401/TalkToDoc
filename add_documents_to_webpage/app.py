# import sys
# import os
#
# # Add the root directory (TalkToDoc) to the Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qdrant_docustore import JinaEmbed
from qdrant_docustore import QdrantLink
from file_to_text import ConvertDocument
import streamlit as st


# Create a basic streamlit app
st.title("Add Documents to Vector Database")
st.write("Upload a document and convert it to text, then add it to the vector database.")