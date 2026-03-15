import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyDRDSI4lOV_Rc2CytUO6yBjlL-lJu88Ovs")
model = genai.GenerativeModel("gemini-2.5-flash")


def extract_requirements(job_description):

    prompt = f"""
Extract the important technical skills and project domains.

Return strictly in this format:

Skills: skill1, skill2, skill3
Projects: project1, project2

JOB DESCRIPTION:
{job_description}
"""

    try:

        response = model.generate_content(prompt)
        text = response.text

        skills = []
        projects = []

        for line in text.split("\n"):

            if "Skills:" in line:
                skills = line.split(":")[1].split(",")

            if "Projects:" in line:
                projects = line.split(":")[1].split(",")

        skills = [s.strip() for s in skills if s.strip()]
        projects = [p.strip() for p in projects if p.strip()]

        return skills, projects

    except:
        return [], []


def evaluate_resume(resume_text, job_description):

    prompt = f"""
You are an HR AI evaluator.

Compare the resume with the job description.

Return response ONLY in this format:

Score: number between 0 and 100
Report: short explanation

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    try:

        response = model.generate_content(prompt)
        text = response.text

        score = 0
        report = text

        for line in text.split("\n"):

            if "Score:" in line:
                try:
                    score = float(line.split(":")[1].strip())
                except:
                    score = 0

        return report, score

    except:
        return "AI evaluation failed", 0