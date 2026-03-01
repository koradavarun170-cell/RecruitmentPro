import streamlit as st
import pandas as pd
import re
import PyPDF2
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import os
import base64

st.markdown("""
<style>

/* Entire text area block */
.stTextArea > div > div {
    background-color: transparent !important;
}

/* Actual textarea */
.stTextArea textarea {
    background-color: transparent !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}

/* Placeholder */
.stTextArea textarea::placeholder {
    color: rgba(255,255,255,0.6) !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Remove white background from main selectbox */
div[data-baseweb="select"] > div {
    background-color: transparent !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
    backdrop-filter: blur(8px);
    color: white !important;
}

/* Text inside selectbox */
div[data-baseweb="select"] span {
    color: white !important;
}

/* Dropdown popup container */
div[role="listbox"] {
    background-color: transparent !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.3);
    color: white !important;
}

/* Each option */
div[role="option"] {
    background-color: transparent !important;
    color: white !important;
}

/* Hover effect */
div[role="option"]:hover {
    background-color: rgba(255,255,255,0.2) !important;
}

</style>
""", unsafe_allow_html=True)

# Function to set background
def set_bg(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()

    page_bg = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

# Call function
set_bg("background.png")
st.markdown("""
    <style>
    .stApp {
        background-color: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(5px);
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# 🔑 Configure Gemini API
# -------------------------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------------
# 🗄 SQLite Database Setup
# -------------------------
def init_db():
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            cgpa REAL,
            final_score REAL,
            ai_decision TEXT,
            resume_text TEXT
        )
    """)

    conn.commit()
    if st.button("🗑 Reset Database"):
        cursor.execute("DELETE FROM candidates")
        conn.commit()
        st.success("Database cleared successfully!")
    conn.close()

init_db()

def save_to_db(name, phone, cgpa, final_score, ai_status, resume_text):
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO candidates (name, phone, cgpa, final_score, ai_decision, resume_text)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, phone, cgpa, final_score, ai_status, resume_text))

    conn.commit()
    conn.close()

# -------------------------
# Streamlit Page Config
# -------------------------
st.set_page_config(page_title="Hybrid AI Recruitment Assistant", layout="wide")
st.title("🤖 Hybrid AI-Powered Recruitment Assistant")
st.markdown("Rule-Based Filtering + Gemini Smart Evaluation + SQLite Storage")

# -------------------------
# UI - Job Requirements
# -------------------------
st.header("📋 Job Requirements")

ALL_SKILLS = [
    "Python","Java","C++","SQL","Machine Learning","Data Science",
    "Cloud","Web Development","AI","Deep Learning","NLP"
]

ALL_PROJECTS = [
    "AI","Web Development","Mobile App","Data Science","Cloud","Cyber Security","ML"
]

required_skills = st.multiselect("🧠 Required Skills", ALL_SKILLS)
required_projects = st.multiselect("📁 Required Project Domains", ALL_PROJECTS)
min_cgpa = st.slider("🎓 Minimum CGPA", 0.0, 10.0, 6.0, 0.1)

# -------------------------
# UI - Job Description
# -------------------------
hr_description = st.text_area(
    "✍️ Full Job Description",
    height=150
)

# -------------------------
# UI - Resume Upload
# -------------------------
uploaded_files = st.file_uploader(
    "📄 Upload Resume PDFs", type=["pdf"], accept_multiple_files=True
)

# -------------------------
# Helper Functions
# -------------------------
def extract_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text.lower()

def extract_cgpa(text):
    matches = re.findall(r"(\d\.\d{1,2})", text)
    for m in matches:
        val = float(m)
        if val <= 10:
            return val
    return 0.0

def extract_name(text):
    lines = text.split("\n")
    for line in lines[:5]:
        clean = line.strip()
        if len(clean.split()) <= 4 and clean.replace(" ", "").isalpha():
            return clean
    return "Unknown"

def extract_phone(text):
    match = re.search(r'\+?\d[\d\s\-]{8,15}', text)
    return match.group(0) if match else "Not Found"

def keyword_filter(text):
    text_lower = text.lower()
    skill_matches = [skill for skill in required_skills if skill.lower() in text_lower]
    project_matches = [proj for proj in required_projects if proj.lower() in text_lower]
    return skill_matches, project_matches

def hr_keywords_filter_dynamic(resume_text, hr_desc, selected_projects):
    resume_text_lower = resume_text.lower()
    hr_desc_lower = hr_desc.lower()

    hr_keywords = [w for w in re.findall(r'\b\w{3,}\b', hr_desc_lower)]
    project_keywords = [p.lower() for p in selected_projects]

    all_keywords = set(hr_keywords + project_keywords)

    for kw in all_keywords:
        if kw in resume_text_lower:
            return True
    return False

def hr_description_score(resume_text, hr_desc):
    if not hr_desc.strip():
        return 0
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, hr_desc])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(similarity * 100, 2)

def gemini_evaluate(resume_text, job_description):
    prompt = f"""
You are an expert HR recruiter.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text[:4000]}

Provide output in this format:

Match Percentage: 0-100
Strengths:
- point1
Missing Skills:
- point1
Final Recommendation: Strong Hire / Consider / Reject
"""
    try:
        response = model.generate_content(prompt)
        result_text = response.text
        match = re.search(r'(\d{1,3})', result_text)
        match_score = int(match.group(1)) if match else 0
        return result_text, match_score
    except Exception as e:
        return f"Error: {str(e)}", 0

# -------------------------
# Main Screening Logic
# -------------------------
if st.button("🚀 Screen Candidates"):

    if not hr_description.strip():
        st.warning("Please enter Job Description.")
    elif not uploaded_files:
        st.warning("Please upload resumes.")
    else:

        results = []

        for file in uploaded_files:
            text = extract_text(file)
            cgpa = extract_cgpa(text)

            if not hr_keywords_filter_dynamic(text, hr_description, required_projects):
                continue

            skill_match, project_match = keyword_filter(text)
            hr_score = hr_description_score(text, hr_description)

            with st.spinner(f"Gemini analyzing {file.name}..."):
                ai_result, ai_score = gemini_evaluate(text, hr_description)

            final_score = round((ai_score*0.5 + hr_score*0.3 + len(skill_match)*5 + len(project_match)*5), 2)

            if final_score < 30:
                ai_status = "Rejected ❌"
            elif final_score < 70:
                ai_status = "Consider 🤔"
            else:
                ai_status = "Strong Hire ✅"

            name = extract_name(text)
            phone = extract_phone(text)

            # Save to SQLite
            save_to_db(name, phone, cgpa, final_score, ai_status, text)

            results.append({
                "Candidate": name,
                "Phone": phone,
                "CGPA": cgpa,
                "Final Score": final_score,
                "AI Decision": ai_status
            })

        if not results:
            st.warning("No resumes matched criteria.")
        else:
            df = pd.DataFrame(results)
            df = df.sort_values(by="Final Score", ascending=False).reset_index(drop=True)

            st.subheader("🏆 Candidate Ranking")
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Ranking CSV",
                csv,
                "Candidate_Ranking.csv",
                "text/csv"
            )

# -------------------------
# View Stored Candidates
# -------------------------
if st.button("📂 View Stored Candidates"):
    conn = sqlite3.connect("candidates.db")
    df_db = pd.read_sql_query("SELECT name, phone, cgpa, final_score, ai_decision FROM candidates", conn)
    conn.close()

    st.subheader("📊 Stored Candidates in Database")
    st.dataframe(df_db, use_container_width=True)

