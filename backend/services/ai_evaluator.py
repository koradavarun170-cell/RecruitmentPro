import re
import google.generativeai as genai

model = genai.GenerativeModel("gemini-2.5-flash")

def gemini_evaluate(resume_text, job_description):

    prompt = f"""
You are an expert HR recruiter.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text[:4000]}

Provide output:

Match Score: 0-100
Strengths:
Missing Skills:
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