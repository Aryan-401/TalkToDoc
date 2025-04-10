from helper import helper_other_file_formats
from helper import helper_jina
import os


class ConvertDocument:

    def __init__(self):
        pass

    def convert_files_to_text(self, file_path: str) -> str:
        """
        Convert a file to text using the helper function.
        """
        # Check if the file exists
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        # Convert the file to text
        text = helper_other_file_formats.convert_other_files_to_markdown(file_path)

        return text

    def convert_webpage_to_text(self, url: str) -> str:
        """
        Convert a webpage to text using the helper function.
        """
        # Convert the webpage to text
        text = helper_jina.helper__web_to_markdown(url)
        return text
