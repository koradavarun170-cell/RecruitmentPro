import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def keyword_filter(text,required_skills,required_projects):
    text_lower = text.lower()

    skill_matches = [s for s in required_skills if s.lower() in text_lower]
    project_matches = [p for p in required_projects if p.lower() in text_lower]

    return skill_matches, project_matches


def hr_keywords_filter(resume_text, hr_desc, selected_projects):

    resume_text = resume_text.lower()
    hr_desc = hr_desc.lower()

    hr_keywords = re.findall(r'\b\w{3,}\b', hr_desc)
    project_keywords = [p.lower() for p in selected_projects]

    all_keywords = set(hr_keywords + project_keywords)

    for kw in all_keywords:
        if kw in resume_text:
            return True

    return False


def hr_description_score(resume_text, hr_desc):

    if not hr_desc.strip():
        return 0

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, hr_desc])

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    return round(similarity * 100, 2)

