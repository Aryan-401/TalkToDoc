
from markitdown import MarkItDown
from groq import Groq


def convert_other_files_to_markdown(file: str) -> str:  # pptx, docx, pdf, jpg, jpeg, png
    client = Groq()
    md = MarkItDown(llm_client=client, llm_model="llama-3.2-90b-vision-preview")
    supported_extensions = ('.pptx', '.docx', '.pdf', '.jpg', '.jpeg', '.png')
    if file.endswith(supported_extensions):
        file_md = md.convert(file)
        return file_md.text_content
