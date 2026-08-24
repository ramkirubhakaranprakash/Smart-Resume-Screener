def score_candidate(candidate_skills, required_skills):
    # Convert skills to lowercase for easy comparison
    candidate_skills = [skill.lower() for skill in candidate_skills]
    required_skills = [skill.lower() for skill in required_skills]

    matched_skills = []

    for skill in required_skills:
        if skill in candidate_skills:
            matched_skills.append(skill)

    missing_skills = []

    for skill in required_skills:
        if skill not in candidate_skills:
            missing_skills.append(skill)

    # Calculate score
    if len(required_skills) == 0:
        score = 0
    else:
        score = round(
            (len(matched_skills) / len(required_skills)) * 100,
            2
        )

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }