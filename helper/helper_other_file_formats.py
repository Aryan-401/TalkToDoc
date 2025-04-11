
from markitdown import MarkItDown
from groq import Groq


def convert_other_files_to_markdown(file: str) -> str:  # pptx, docx, pdf, jpg, jpeg, png
    client = Groq()
    md = MarkItDown(llm_client=client, llm_model="meta-llama/llama-4-scout-17b-16e-instruct")
    supported_extensions = ('.pptx', '.docx', '.pdf', '.jpg', '.jpeg', '.png')
    if file.endswith(supported_extensions):
        file_md = md.convert(file)
        return file_md.text_content
