from fastapi import FastAPI, UploadFile, File, Form
from typing import List
from services import ai_evaluator, candidate_matching, resume_parser
from models import candidate_model
from database.db import session,engine

app = FastAPI()

candidate_model.Base.metadata.create_all(bind=engine)

@app.post("/screen_candidates")
async def screen_candidates(
    files: List[UploadFile] = File(...),
    job_description: str = Form(...),
    required_skills: str = Form(...),
    required_projects: str = Form(...)
):

    required_skills = [s for s in required_skills.split(",") if s]
    required_projects = [p for p in required_projects.split(",") if p]

    results = []

    for file in files:

        resume_text = resume_parser.extract_text(file)
        cgpa = resume_parser.extract_cgpa(resume_text)

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
        
        if final_score < 40:
            decision = "Rejected"
        elif final_score < 70:
            decision = "Consider"
        else:
            decision = "Strong Hire"

        results.append({
            "candidate": file.filename,
            "cgpa": cgpa,
            "skill_matches": skill_match,
            "project_matches": project_match,
            "ai_score": ai_score,
            "hr_score": hr_score,
            "final_score": final_score,
            "decision": decision,
            "ai_report": ai_result
        })

    return {"results": results}
@app.post("/store_candidates")
async def store_candidates(data: dict):
    results = data["results"]
    job_role = data["job_role"]
    db = session()
    for result in results:
        candidate = candidate_model.Candidate(
            name=result["candidate"],
            job_role=job_role,
            final_score=result["final_score"]
        )

        db.add(candidate)

    db.commit()
    db.close()

    return {"message": "Candidates stored successfully"}