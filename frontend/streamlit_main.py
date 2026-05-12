import streamlit as st
import pandas as pd
import requests
import base64


st.set_page_config(page_title="AI Recruitment Assistant", layout="wide")


# ---------------- BACKGROUND ----------------
def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


set_bg("background.png")


# ---------------- UI STYLE ----------------
st.markdown("""
<style>
textarea, input, select {
    background-color: rgba(0,0,0,0.3) !important;
    color: white !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------- TITLE ----------------
st.title("🤖 AI-Powered Recruitment Assistant")
st.markdown("Resume Filtering + AI Candidate Evaluation")


# ---------------- INPUTS ----------------
st.header("📋 Job Requirements")

ALL_SKILLS = [
    "Python","Java","C++","SQL","Machine Learning","Data Science",
    "Cloud","Web Development","AI","Deep Learning","NLP"
]

ALL_PROJECTS = [
    "AI","Web Development","Mobile App","Data Science",
    "Cloud","Cyber Security","ML"
]

required_skills = st.multiselect("Required Skills", ALL_SKILLS)
required_projects = st.multiselect("Project Domains", ALL_PROJECTS)

min_cgpa = st.slider("Minimum CGPA", 0.0, 10.0, 6.0)

hr_description = st.text_area("Job Description", height=150)

uploaded_files = st.file_uploader(
    "Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)


# ---------------- BUTTON ACTION ----------------
if st.button("🚀 Screen Candidates"):

    if not hr_description.strip():
        st.warning("Please enter job description.")
        st.stop()

    if not uploaded_files:
        st.warning("Please upload resumes.")
        st.stop()

    with st.spinner("Screening candidates..."):

        # FILES (IMPORTANT)
        files = [
            ("files", (file.name, file, "application/pdf"))
            for file in uploaded_files
        ]

        # FORM DATA (IMPORTANT)
        data = {
            "job_description": hr_description,
            "required_skills": ",".join(required_skills),
            "required_projects": ",".join(required_projects),
            "min_cgpa": str(min_cgpa)   # ✅ FIX FOR 422 ERROR
        }

        # API CALL
        response = requests.post(
            "http://127.0.0.1:8000/screen_candidates",
            files=files,
            data=data
        )

    # ---------------- RESPONSE HANDLING ----------------
    if response.status_code != 200:
        st.error(f"Backend error: {response.text}")
        st.stop()

    results = response.json().get("results", [])

    if not results:
        st.warning("No resumes matched criteria.")
        st.stop()

    # ---------------- DISPLAY RESULTS ----------------
    df = pd.DataFrame(results)
    df = df.sort_values(by="final_score", ascending=False)

    st.subheader("🏆 Candidate Ranking")
    st.dataframe(df, use_container_width=True)

    # Download CSV
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Report",
        csv,
        "candidate_report.csv",
        "text/csv"
    )