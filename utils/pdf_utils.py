import logging
import re
from langchain_community.document_loaders import PyPDFLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text(file_path):
    try:
        logger.info(f"Extracting text from {file_path}")
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        text = " ".join([doc.page_content for doc in docs]).lower()
        text = " ".join(text.split())
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {str(e)}")
        return ""

def extract_links_and_contact(text):
    try:
        logger.info("Extracting contact info")
        data = {}
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        data["email"] = re.findall(email_pattern, text)

        # Phone number (Indian format or general 10-digit)
        phone_pattern = r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b"
        data["phone"] = re.findall(phone_pattern, text)

        # LinkedIn (matches both with and without https)
        linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_]+"
        data["linkedin"] = re.findall(linkedin_pattern, text)

        # GitHub (matches both with and without https)
        github_pattern = r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9\-_]+"
        data["github"] = re.findall(github_pattern, text)
        return data
    except Exception as e:
        logger.error(f"Error extracting contact info: {str(e)}")
        return {"email": [], "phone": [], "linkedin": [], "github": []}