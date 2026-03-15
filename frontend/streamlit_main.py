import streamlit as st
import pandas as pd
import requests
import base64
from backend import *
st.set_page_config(page_title="AI Recruitment Assistant", layout="wide")


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


st.markdown("""
<style>
textarea, input, select {
    background-color: rgba(255,255,255,0.15) !important;
    color: white !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


st.title("🤖 AI-Powered Recruitment Assistant")
st.markdown("Resume Filtering + AI Candidate Evaluation")


st.header("📋 Job Requirements")


ALL_SKILLS = [
    "Python","Java","C++","SQL","Machine Learning","Data Science",
    "Cloud","Web Development","AI","Deep Learning","NLP"
]

ALL_PROJECTS = [
    "AI","Web Development","Mobile App","Data Science",
    "Cloud","Cyber Security","ML"
]


required_skills = st.multiselect("Required Skills", ALL_SKILLS,)

required_projects = st.multiselect("Project Domains", ALL_PROJECTS)

min_cgpa = st.slider("Minimum CGPA", 0.0, 10.0, 6.0)


hr_description = st.text_area(
    "Job Description",
    height=150
)


uploaded_files = st.file_uploader(
    "Upload Resume PDFs",
    type=["pdf","docx"],
    accept_multiple_files=True
)


if st.button("🚀 Screen Candidates"):

    if not hr_description.strip():
        st.warning("Please enter job description.")

    elif not uploaded_files:
        st.warning("Please upload resumes.")

    else:

        with st.spinner("Screening candidates..."):

            files = [
                ("files", (file.name, file, "application/pdf"))
                for file in uploaded_files
            ]

            data = {
                "job_description": hr_description,
                "required_skills": ",".join(required_skills),
                "required_projects": ",".join(required_projects)
            }

            response = requests.post(
                "http://127.0.0.1:8000/screen_candidates",
                files=files,
                data=data
            )

            if response.status_code != 200:
                st.error("Backend error")
                st.stop()

            results = response.json()["results"]

        if not results:
            st.warning("No resumes matched criteria.")

        else:

            df = pd.DataFrame(results)

            df = df.sort_values(by="final_score", ascending=False)

            st.session_state["results_df"] = df

            st.subheader("🏆 Candidate Ranking")

            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download Report",
                csv,
                "candidate_report.csv",
                "text/csv"
            )

st.subheader("📅 Schedule Interview")

candidate_name = st.text_input("Candidate Name")

interview_date = st.date_input("Interview Date")

interview_time = st.time_input("Interview Time")

if st.button("Schedule Interview"):

    payload = {
        "candidate_name": candidate_name,
        "date": str(interview_date),
        "time": str(interview_time)
    }

    response = requests.post(
        "http://127.0.0.1:8000/schedule_interview",
        json=payload
    )

    if response.status_code == 200:
        st.success("Interview Scheduled Successfully!")
    else:
        st.error("Failed to schedule interview")



st.subheader("📧 Generate Candidate Communication")

candidate_name_msg = st.text_input("Candidate Name for Message")

decision_msg = st.selectbox(
    "Decision",
    ["Strong Hire", "Consider", "Rejected"]
)

role_msg = st.text_input("Role for Message")

if st.button("Generate Message"):

    payload = {
        "name": candidate_name_msg,
        "role": role_msg,
        "decision": decision_msg
    }

    response = requests.post(
        "http://127.0.0.1:8000/generate_message",
        json=payload
    )

    if response.status_code == 200:
        st.text_area("Generated Message", response.json()["message"], height=200)




st.subheader("💾 Store Results in Database")

job_role = st.text_input("Job Role (for storing results)")

if st.button("Store Results"):

    if "results_df" not in st.session_state:
        st.warning("Run candidate screening first.")

    elif not job_role.strip():
        st.warning("Please enter the job role.")

    else:

        df = st.session_state["results_df"]

        payload = {
            "job_role": job_role,
            "results": df.to_dict(orient="records")
        }

        store_response = requests.post(
            "http://127.0.0.1:8000/store_candidates",
            json=payload
        )

        if store_response.status_code == 200:
            st.success("Results stored successfully!")
        else:
            st.error("Failed to store results.")
