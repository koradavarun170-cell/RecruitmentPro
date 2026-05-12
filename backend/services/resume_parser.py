import PyPDF2
import re


def extract_text(file):
    """
    Extract text from FastAPI UploadFile or file-like object
    """

    # ✅ IMPORTANT FIX: use file.file for FastAPI UploadFile
    reader = PyPDF2.PdfReader(file.file)

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted + " "

    return text.lower().strip()


def extract_cgpa(text):
    """
    Extract CGPA safely from resume text
    """

    matches = re.findall(r"(\d\.\d{1,2})", text)

    for m in matches:
        val = float(m)

        if 0 <= val <= 10:
            return val

    return 0.0