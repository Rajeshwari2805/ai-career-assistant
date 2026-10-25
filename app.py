import ollama
import json

# -----------------------------
# 1. Get user input
# -----------------------------

resume = input("Paste your resume: ")
job_description = input("Paste the job description: ")


# -----------------------------
# 2. AI prompt
# -----------------------------

prompt = f"""
You are an AI Career Assistant.

Compare the candidate's resume with the job description.

Resume:
{resume}

Job Description:
{job_description}

Rules:

1. Identify the important requirements explicitly mentioned in the job description.
2. Identify which requirements are clearly present in the resume.
3. Put matched requirements in "matching_skills".
4. Put genuinely missing requirements in "missing_skills".
5. Do not invent requirements.
6. Treat equivalent education correctly.
   Example:
   B.Tech Computer Science = Bachelor's degree in Computer Science.
7. If the resume contains JSON, consider JSON a match when JSON is required.
8. If the resume contains API knowledge, do NOT automatically consider it
   a match for REST API experience.
9. Related skills must be judged carefully.
10. Do not calculate the match score.
11. Keep each skill as a short, clear requirement.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "matching_skills": [],
    "missing_skills": [],
    "recommendations": []
}}
"""


# -----------------------------
# 3. Ask Ollama
# -----------------------------

response = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)


# -----------------------------
# 4. Get AI response
# -----------------------------

raw_response = response["message"]["content"]


# -----------------------------
# 5. Process response
# -----------------------------

try:

    result = json.loads(raw_response)

    matching_skills = result["matching_skills"]
    missing_skills = result["missing_skills"]
    recommendations = result["recommendations"]


    # -----------------------------
    # 6. Simple normalization rules
    # -----------------------------

    resume_lower = resume.lower()

    # JSON normalization
    if "json" in resume_lower:

        missing_skills = [
            skill
            for skill in missing_skills
            if "json" not in skill.lower()
        ]

        if not any("json" in skill.lower() for skill in matching_skills):
            matching_skills.append("JSON")


    # Bachelor's degree normalization
    if (
        "b.tech" in resume_lower
        or "btech" in resume_lower
        or "bachelor" in resume_lower
    ) and "computer science" in resume_lower:

        missing_skills = [
            skill
            for skill in missing_skills
            if not (
                "bachelor" in skill.lower()
                and "computer" in skill.lower()
            )
        ]

        if not any(
            "bachelor" in skill.lower()
            and "computer" in skill.lower()
            for skill in matching_skills
        ):
            matching_skills.append(
                "Bachelor's degree in Computer Science"
            )


    # -----------------------------
    # 7. Calculate score with Python
    # -----------------------------

    total_requirements = (
        len(matching_skills) +
        len(missing_skills)
    )

    if total_requirements > 0:
        match_score = round(
            len(matching_skills)
            / total_requirements
            * 100
        )
    else:
        match_score = 0


    # -----------------------------
    # 8. Display results
    # -----------------------------

    print("\n========== CAREER ANALYSIS ==========")

    print(f"\nMatch Score: {match_score}%")

    print("\nMatching Skills:")

    if matching_skills:
        for skill in matching_skills:
            print("✓", skill)
    else:
        print("None")


    print("\nMissing Skills:")

    if missing_skills:
        for skill in missing_skills:
            print("•", skill)
    else:
        print("None")


    print("\nRecommendations:")

    if recommendations:
        for recommendation in recommendations:
            print("→", recommendation)
    else:
        print("No recommendations needed.")


# -----------------------------
# 9. Error handling
# -----------------------------

except json.JSONDecodeError:

    print("\nThe AI returned invalid JSON.")
    print("\nRaw AI response:")
    print(raw_response)


except KeyError as error:

    print(f"\nMissing field in AI response: {error}")
    print("\nRaw AI response:")
    print(raw_response)