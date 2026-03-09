import PyPDF2
import re

import PyPDF2

def extract_text(file):

    reader = PyPDF2.PdfReader(file.file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    return text

def extract_cgpa(text):
    matches = re.findall(r"(\d\.\d{1,2})", text)

    for m in matches:
        val = float(m)
        if val <= 10:
            return val

    return 0.0