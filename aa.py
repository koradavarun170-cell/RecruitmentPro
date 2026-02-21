import streamlit as st
import PyPDF2
import spacy
import re

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="Resume Shortlisting System",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Resume Shortlisting System")
st.markdown("""
Upload multiple resumes and shortlist candidates based on:
- At least 2 skills from C, C++, Java, Python
- Minimum CGPA 8.0
""")

# ---------------- LOAD SPACY ----------------
@st.cache_resource
def load_spacy_model():
    return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("📄 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload candidate resumes (PDF)",
        type=["pdf"],
        accept_multiple_files=True
    )

# ---------------- CONFIG ----------------
REQUIRED_SKILLS = ["c", "c++", "java", "python"]
MIN_SKILLS = 2
MIN_CGPA = 8.0

# ---------------- FUNCTIONS ----------------
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_candidate_name(resume_text):
    """Extract candidate name: assume in first 3 lines, up to 4 words"""
    lines = resume_text.split("\n")
    for line in lines[:3]:
        line = line.strip()
        if line and len(line.split()) <= 4:
            return line
    return "Name not found"

def extract_skills(resume_text):
    resume_text_lower = resume_text.lower()
    matched = [s.upper() for s in REQUIRED_SKILLS if s in resume_text_lower]
    return matched

def extract_cgpa(resume_text):
    """
    Extract CGPA from resume text safely.
    Looks for numbers near 'cgpa' (case-insensitive) or inside parentheses.
    Returns float, 0.0 if not found
    """
    matches = re.findall(r'(\d\.\d+)\s*(?:cgpa)?', resume_text, re.I)
    if matches:
        for m in matches:
            val = float(m)
            if val <= 10.0:
                return val
    return 0.0

# ---------------- MAIN LOGIC ----------------
if uploaded_files:
    st.subheader("📋 Shortlisting Results")

    shortlisted = []
    rejected = []

    for file in uploaded_files:
        resume_text = extract_text_from_pdf(file)
        candidate_name = extract_candidate_name(resume_text)
        skills_matched = extract_skills(resume_text)
        cgpa = extract_cgpa(resume_text)

        # Apply criteria
        if len(skills_matched) >= MIN_SKILLS and cgpa >= MIN_CGPA:
            shortlisted.append({
                "name": candidate_name,
                "skills": skills_matched,
                "cgpa": cgpa
            })
        else:
            rejected.append({
                "name": candidate_name,
                "skills": skills_matched,
                "cgpa": cgpa
            })

    # -------- DISPLAY SHORTLISTED --------
    st.success(f"✅ Shortlisted Candidates ({len(shortlisted)})")
    if shortlisted:
        for i, c in enumerate(shortlisted, 1):
            st.write(f"**{i}. {c['name']}** — Skills: {', '.join(c['skills'])}, CGPA: {c['cgpa']}")
    else:
        st.write("No candidates shortlisted.")

    # -------- DISPLAY REJECTED --------
    st.error(f"❌ Rejected Candidates ({len(rejected)})")
    if rejected:
        for i, c in enumerate(rejected, 1):
            st.write(f"{i}. {c['name']} — Skills: {', '.join(c['skills'])}, CGPA: {c['cgpa']}")

else:
    st.info("👈 Upload multiple PDF resumes to begin shortlisting.")
