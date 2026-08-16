def normalize_skill(skill: str) -> str:
    return skill.strip().lower()


def calculate_match(
    resume_skills: list[str],
    required_skills: list[str]
) -> dict:

    resume_normalized = {
        normalize_skill(skill)
        for skill in resume_skills
    }

    matched_skills = []
    missing_skills = []

    for skill in required_skills:
        normalized = normalize_skill(skill)

        if normalized in resume_normalized:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    total_required = len(required_skills)

    if total_required == 0:
        score = 0.0
    else:
        score = (len(matched_skills) / total_required) * 100

    return {
        "score": round(score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }