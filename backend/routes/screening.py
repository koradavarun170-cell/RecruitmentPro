from fastapi import APIRouter, UploadFile, File, Form
from typing import List

from services import ai_evaluator, candidate_matching, resume_parser

router = APIRouter()


@router.post("/screen_candidates")
async def screen_candidates(
    files: List[UploadFile] = File(...),
    job_description: str = Form(...),
    required_skills: str = Form(""),
    required_projects: str = Form(""),
    min_cgpa: float = Form(0.0)   # ✅ default added to prevent 422 issues
):

    required_skills = [
        s.strip() for s in required_skills.split(",") if s.strip()
    ] if required_skills else []

    required_projects = [
        p.strip() for p in required_projects.split(",") if p.strip()
    ] if required_projects else []

    results = []

    for file in files:

        resume_text = resume_parser.extract_text(file)

        cgpa = resume_parser.extract_cgpa(resume_text)

        # CGPA filter
        if cgpa < min_cgpa:
            continue

        # HR filter
        if not candidate_matching.hr_keywords_filter(
            resume_text,
            job_description,
            required_projects
        ):
            continue

        skill_match, project_match = candidate_matching.keyword_filter(
            resume_text,
            required_skills,
            required_projects
        )

        hr_score = candidate_matching.hr_description_score(
            resume_text,
            job_description
        )

        ai_result, ai_score = ai_evaluator.gemini_evaluate(
            resume_text,
            job_description
        )

        final_score = round(
            ai_score * 0.5 +
            hr_score * 0.3 +
            len(skill_match) * 5 +
            len(project_match) * 5,
            2
        )

        results.append({
            "candidate": file.filename,
            "cgpa": cgpa,
            "skill_matches": ", ".join(skill_match),
            "project_matches": ", ".join(project_match),
            "ai_score": ai_score,
            "hr_score": hr_score,
            "final_score": final_score,
            "ai_report": ai_result
        })

    return {"results": results}