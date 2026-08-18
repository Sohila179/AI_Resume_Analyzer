# def normalize_skill(skill: str) -> str:
#     return skill.strip().lower()


# def analyze_skill_gap(
#     resume_skills: list[str],
#     required_skills: list[str]
# ):
#     resume_normalized = {
#         normalize_skill(skill): skill
#         for skill in resume_skills
#     }

#     required_normalized = {
#         normalize_skill(skill): skill
#         for skill in required_skills
#     }

#     matched_skills = []

#     for skill in required_normalized:
#         if skill in resume_normalized:
#             matched_skills.append(
#                 required_normalized[skill]
#             )

#     missing_skills = []

#     for skill in required_normalized:
#         if skill not in resume_normalized:
#             missing_skills.append(
#                 required_normalized[skill]
#             )

#     return {
#         "matched_skills": matched_skills,
#         "missing_skills": missing_skills
#     }
def analyze_skill_gap(user_skills, required_skills):

    user_skills = {
        skill.strip().lower()
        for skill in user_skills
    }

    required_skills = {
        skill.strip().lower()
        for skill in required_skills
    }

    matched_skills = required_skills & user_skills

    missing_skills = required_skills - user_skills

    return {
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills)
    }