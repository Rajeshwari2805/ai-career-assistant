import json
import re

import streamlit as st

try:
    import ollama
except ImportError:
    ollama = None


st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🎯",
    layout="wide",
)

st.title("AI Career Assistant")
st.write(
    "Compare your resume with a job description, identify skill gaps, "
    "and get a personalized learning roadmap."
)


SKILL_PATTERNS = {
    "Bachelor's degree in Computer Science": [
        r"\bbachelor(?:'s)?\s+(?:degree\s+)?(?:in\s+)?"
        r"(?:computer science|computer engineering|information technology)\b",
        r"\bb\.?\s*tech\b",
        r"\bb\.?\s*e\.?\s*(?:cse|computer science)\b",
        r"\bb\.?\s*sc\.?\s*(?:computer science|it)\b",
        r"\bcomputer science(?: and engineering)?\b",
    ],
    "Python": [r"\bpython\b"],
    "REST APIs": [
        r"\brest(?:ful)?\s*apis?\b",
        r"\bhttp\s+methods?\b",
        r"\bapi integration\b",
        r"\brest api development\b",
    ],
    "JSON": [r"\bjson\b", r"\bjavascript object notation\b"],
    "SQL / Databases": [
        r"\bsql\b",
        r"\bdatabases?\b",
        r"\bmysql\b",
        r"\bpostgres(?:ql)?\b",
        r"\bsqlite\b",
        r"\bdatabase concepts\b",
    ],
    "HTML / CSS / JavaScript": [
        r"\bhtml\b",
        r"\bcss\b",
        r"\bjavascript\b",
        r"\bfront[- ]end development\b",
    ],
    "Git / GitHub": [
        r"\bgit(?:hub)?\b",
        r"\bversion control\b",
    ],
    "Problem Solving": [
        r"\bproblem[- ]solving\b",
        r"\blogical thinking\b",
        r"\banalytical thinking\b",
        r"\banalytical skills\b",
    ],
    "Generative AI": [
        r"\bgenerative ai\b",
        r"\bgen ai\b",
        r"\bgenai\b",
    ],
    "LLMs": [
        r"\blarge language models?\b",
        r"\bllms?\b",
    ],
    "Prompt Engineering": [
        r"\bprompt engineering\b",
        r"\bprompt design\b",
    ],
    "AI Tools / LLM APIs": [
        r"\bllm apis?\b",
        r"\bai tools\b",
        r"\bai application development\b",
        r"\bllm integration\b",
        r"\bapplications? using ai tools\b",
    ],
    "RAG": [
        r"\bretrieval[- ]augmented generation\b",
        r"\brag\b",
    ],
    "Streamlit": [
        r"\bstreamlit\b",
        r"\bapplication frameworks?\b",
    ],
}


LEARNING_GUIDE = {
    "REST APIs": {
        "effort": "3–5 days",
        "focus": "HTTP methods, endpoints, status codes, requests and responses.",
        "steps": [
            "Understand GET, POST, PUT, PATCH and DELETE.",
            "Learn HTTP status codes, headers and request bodies.",
            "Use Python requests to call a public test API.",
        ],
        "project": "Build a Python application that fetches and displays API data.",
    },
    "JSON": {
        "effort": "1–2 days",
        "focus": "JSON objects, arrays, nested values and Python's json module.",
        "steps": [
            "Understand JSON objects, arrays, strings, numbers and booleans.",
            "Practise reading and writing JSON using Python.",
            "Handle missing fields and invalid JSON safely.",
        ],
        "project": "Build a program that reads a JSON file and summarizes its contents.",
    },
    "Python": {
        "effort": "5–7 days",
        "focus": "Variables, conditions, loops, functions, lists, dictionaries and files.",
        "steps": [
            "Review Python syntax, data types and control flow.",
            "Practise functions, lists and dictionaries.",
            "Build a small program that reads and processes data.",
        ],
        "project": "Build a Python resume keyword checker.",
    },
    "SQL / Databases": {
        "effort": "4–6 days",
        "focus": "Tables, keys, SELECT, filtering, joins and database concepts.",
        "steps": [
            "Review tables, primary keys and foreign keys.",
            "Practise SELECT, WHERE, ORDER BY and GROUP BY.",
            "Learn basic joins and insert/update operations.",
        ],
        "project": "Create a small job application tracker database.",
    },
    "HTML / CSS / JavaScript": {
        "effort": "5–7 days",
        "focus": "HTML structure, CSS styling and basic JavaScript interactions.",
        "steps": [
            "Create a simple page using HTML.",
            "Style the page with CSS.",
            "Use JavaScript to handle a basic user interaction.",
        ],
        "project": "Build a simple personal portfolio webpage.",
    },
    "Git / GitHub": {
        "effort": "1–2 days",
        "focus": "Repositories, commits, branches and pushing code to GitHub.",
        "steps": [
            "Learn git init, status, add and commit.",
            "Create a GitHub repository.",
            "Push your project and write a clear README.",
        ],
        "project": "Upload your AI Career Assistant project to GitHub.",
    },
    "Problem Solving": {
        "effort": "3–5 days",
        "focus": "Breaking problems into smaller steps and testing solutions.",
        "steps": [
            "Practise writing steps before coding.",
            "Solve beginner logic and string problems.",
            "Test normal cases and edge cases.",
        ],
        "project": "Create a program that validates job application data.",
    },
    "Generative AI": {
        "effort": "5–7 days",
        "focus": "Generative models, common use cases and limitations.",
        "steps": [
            "Understand the basics of generative AI.",
            "Compare common AI application use cases.",
            "Learn about hallucinations, privacy and evaluation.",
        ],
        "project": "Build an AI tool that summarizes a job description.",
    },
    "LLMs": {
        "effort": "3–5 days",
        "focus": "Tokens, context windows, model outputs and limitations.",
        "steps": [
            "Learn what tokens and context windows are.",
            "Compare model responses to the same task.",
            "Check generated answers for accuracy.",
        ],
        "project": "Build a question-answering assistant using a local LLM.",
    },
    "Prompt Engineering": {
        "effort": "2–3 days",
        "focus": "Clear instructions, context, examples and output formats.",
        "steps": [
            "Write prompts with a clear task and context.",
            "Try examples and structured output instructions.",
            "Compare and evaluate different prompt versions.",
        ],
        "project": "Create a prompt template that extracts skills from job descriptions.",
    },
    "AI Tools / LLM APIs": {
        "effort": "3–5 days",
        "focus": "Calling AI models, passing inputs and handling outputs.",
        "steps": [
            "Understand model inputs and generated outputs.",
            "Make a simple call to a local model or an available API.",
            "Handle errors and validate returned data.",
        ],
        "project": "Build an AI-powered job description summarizer.",
    },
    "RAG": {
        "effort": "5–7 days",
        "focus": "Documents, chunking, embeddings, retrieval and grounded answers.",
        "steps": [
            "Understand how retrieval helps answer questions about documents.",
            "Learn the roles of document chunks and embeddings.",
            "Build a workflow that retrieves relevant text before answering.",
        ],
        "project": "Build a question-answering tool over your resume or notes.",
    },
    "Streamlit": {
        "effort": "2–3 days",
        "focus": "Inputs, buttons, session state and presenting results.",
        "steps": [
            "Learn text areas, buttons and other Streamlit widgets.",
            "Display results and handle missing input.",
            "Organize an app into clear sections.",
        ],
        "project": "Improve your AI Career Assistant interface.",
    },
    "Bachelor's degree in Computer Science": {
        "effort": "Existing qualification",
        "focus": "Present your completed degree accurately in your resume.",
        "steps": [
            "Add your degree, institution and graduation year.",
            "Keep your CGPA consistent with official records.",
            "Ensure the education section is easy to find.",
        ],
        "project": "Update the education section of your resume.",
    },
}


def find_skills(text):
    """Return canonical skills detected in text."""
    found = []

    for skill, patterns in SKILL_PATTERNS.items():
        if any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in patterns
        ):
            found.append(skill)

    return found


def canonicalize_skill(skill):
    """Normalize a model-extracted skill to a known skill label."""
    text = str(skill).strip()
    matches = find_skills(text)

    if matches:
        return matches[0]

    return text


def normalize_heading(line):
    """Normalize common Markdown and plain-text section headings."""
    line = line.strip()
    line = re.sub(r"^\s*[-*•#]+\s*", "", line)
    line = re.sub(r"^\*\*(.*?)\*\*$", r"\1", line)
    line = line.strip().strip("*").strip()
    line = re.sub(r":\s*$", "", line)

    return line.lower().strip()


def extract_heading_section(text, heading_aliases, following_headings):
    """Extract a section using its heading and the next recognized heading."""
    lines = text.splitlines()
    start = None
    end = len(lines)

    aliases = {normalize_heading(h) for h in heading_aliases}
    endings = {normalize_heading(h) for h in following_headings}

    for index, line in enumerate(lines):
        if normalize_heading(line) in aliases:
            start = index + 1
            break

    if start is None:
        return ""

    for index in range(start, len(lines)):
        if normalize_heading(lines[index]) in endings:
            end = index
            break

    return "\n".join(lines[start:end]).strip()


def extract_job_requirements(job_description):
    """Extract required and preferred skills separately when headings exist."""

    required_section = extract_heading_section(
        job_description,
        [
            "Required Skills",
            "Required",
            "Mandatory Skills",
            "Must Have Skills",
        ],
        [
            "Preferred Skills",
            "Preferred",
            "Nice to Have",
            "Responsibilities",
            "Experience",
            "Qualifications",
            "About the Role",
        ],
    )

    preferred_section = extract_heading_section(
        job_description,
        [
            "Preferred Skills",
            "Preferred",
            "Nice to Have",
            "Good to Have",
        ],
        [
            "Required Skills",
            "Required",
            "Mandatory Skills",
            "Must Have Skills",
            "Responsibilities",
            "Experience",
            "Qualifications",
            "About the Role",
        ],
    )

    # Use the explicit sections when at least one is found.
    if required_section or preferred_section:
        required = find_skills(required_section)
        preferred = find_skills(preferred_section)

        # A required skill should not also be counted as preferred.
        preferred = [
            skill for skill in preferred
            if skill not in required
        ]

        return required, preferred

    # Fallback for job descriptions without recognizable skill headings.
    detected = find_skills(job_description)
    required = []
    preferred = []

    preferred_terms = (
        "preferred",
        "nice to have",
        "bonus",
        "a plus",
        "desirable",
        "advantage",
        "familiarity with",
        "good to have",
    )

    for skill in detected:
        occurrences = []

        for pattern in SKILL_PATTERNS[skill]:
            for match in re.finditer(
                pattern, job_description, re.IGNORECASE
            ):
                context = job_description[
                    max(0, match.start() - 90):
                    min(len(job_description), match.end() + 90)
                ].lower()

                occurrences.append(context)

        is_preferred = any(
            term in context
            for context in occurrences
            for term in preferred_terms
        )

        if is_preferred:
            preferred.append(skill)
        else:
            required.append(skill)

    return required, preferred


def extract_resume_skills(resume_text):
    """Detect resume skills using regex and optionally local Ollama."""
    detected = find_skills(resume_text)

    if ollama is None or not resume_text.strip():
        return detected

    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract only skills supported by the resume text. "
                        "Return a JSON object with a 'skills' array. "
                        "Do not invent skills or infer skills from "
                        "the job requirements."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Known skill labels: "
                        + ", ".join(SKILL_PATTERNS.keys())
                        + "\n\nResume:\n"
                        + resume_text[:12000]
                    ),
                },
            ],
            format="json",
            options={"temperature": 0},
        )

        data = json.loads(response["message"]["content"])
        model_skills = data.get("skills", [])

        if isinstance(model_skills, list):
            for item in model_skills:
                skill = canonicalize_skill(item)

                if (
                    skill in SKILL_PATTERNS
                    and skill not in detected
                ):
                    detected.append(skill)

    except Exception:
        # Keep regex detection available if Ollama is unavailable or errors.
        pass

    return detected


def calculate_match(required, preferred, resume_skills):
    """Calculate the keyword match score and skill gaps."""
    resume_set = set(resume_skills)

    matching_required = [
        skill for skill in required if skill in resume_set
    ]
    missing_required = [
        skill for skill in required if skill not in resume_set
    ]
    matching_preferred = [
        skill for skill in preferred if skill in resume_set
    ]
    missing_preferred = [
        skill for skill in preferred if skill not in resume_set
    ]

    # Required skills contribute 70%; preferred skills contribute 30%.
    total_weight = 0
    earned_weight = 0

    if required:
        total_weight += 70
        earned_weight += (
            70 * len(matching_required) / len(required)
        )

    if preferred:
        total_weight += 30
        earned_weight += (
            30 * len(matching_preferred) / len(preferred)
        )

    score = (
        round(100 * earned_weight / total_weight)
        if total_weight
        else 0
    )

    return {
        "score": score,
        "matching_required": matching_required,
        "missing_required": missing_required,
        "matching_preferred": matching_preferred,
        "missing_preferred": missing_preferred,
    }


def show_roadmap(skill, category):
    """Display learning guidance for one missing skill."""
    guide = LEARNING_GUIDE.get(skill)

    st.write(f"**{skill}** — {category.capitalize()} skill")

    if not guide:
        st.write(
            "Learn the fundamentals, then practise with a small "
            "hands-on exercise."
        )
        return

    st.write(f"Estimated effort: {guide['effort']}")
    st.write(f"Focus: {guide['focus']}")
    st.write("Suggested steps:")

    for step in guide["steps"]:
        st.write(f"- {step}")

    st.write(f"Practice project: {guide['project']}")


# Resume input
st.subheader("1. Enter your resume")

resume_text = st.text_area(
    "Paste your resume text",
    height=250,
    placeholder=(
        "Paste your education, skills, projects, internships "
        "and experience here..."
    ),
)

# Job description input
st.subheader("2. Enter the job description")

job_description = st.text_area(
    "Paste the complete job description",
    height=300,
    placeholder=(
        "Include the job title, required skills, preferred skills "
        "and responsibilities..."
    ),
)

analyze_button = st.button(
    "Analyze Resume",
    type="primary",
)


if analyze_button:
    if not resume_text.strip() or not job_description.strip():
        st.warning(
            "Please enter both your resume and the job description."
        )

    else:
        required, preferred = extract_job_requirements(
            job_description
        )
        resume_skills = extract_resume_skills(resume_text)

        if not required and not preferred:
            st.warning(
                "No recognized skills were found in the job description. "
                "Include the full Required Skills and Preferred Skills "
                "sections, or check whether the description mentions "
                "skills supported by this app."
            )

        else:
            results = calculate_match(
                required,
                preferred,
                resume_skills,
            )

            st.divider()
            st.subheader("Career Match Results")

            st.write(
                f"**Career Match Score: {results['score']}%**"
            )
            st.progress(results["score"] / 100)

            if results["score"] >= 80:
                st.success(
                    "Strong keyword match. Review the remaining gaps "
                    "and ensure your resume demonstrates these skills."
                )
            elif results["score"] >= 60:
                st.info(
                    "Partial keyword match. Review the missing skills below."
                )
            else:
                st.warning(
                    "Several job-description skills were not detected "
                    "in your resume."
                )

            st.caption(
                "The score measures detected keyword matches against "
                "the job requirements. It is not a probability of "
                "getting hired or a measure of actual ability."
            )

            st.subheader("Required Skills")

            if required:
                for skill in required:
                    st.write(f"- {skill}")
            else:
                st.write("No required skills were detected.")

            st.subheader("Matching Required Skills")

            if results["matching_required"]:
                for skill in results["matching_required"]:
                    st.write(f"- {skill}")
            else:
                st.write("No required skills matched your resume keywords.")

            st.subheader("Missing Required Skills")

            if results["missing_required"]:
                for skill in results["missing_required"]:
                    st.write(f"- {skill}")
            else:
                st.write("No missing required skills were detected.")

            st.subheader("Preferred Skills")

            if preferred:
                for skill in preferred:
                    st.write(f"- {skill}")
            else:
                st.write("No preferred skills were detected.")

            st.subheader("Matching Preferred Skills")

            if results["matching_preferred"]:
                for skill in results["matching_preferred"]:
                    st.write(f"- {skill}")
            else:
                st.write("No preferred skills matched your resume keywords.")

            st.subheader("Missing Preferred Skills")

            if results["missing_preferred"]:
                for skill in results["missing_preferred"]:
                    st.write(f"- {skill}")
            else:
                st.write("No missing preferred skills were detected.")

            st.divider()
            st.subheader("Recommendations")

            if results["missing_required"]:
                st.write(
                    "Prioritize the missing required skills first:"
                )

                for skill in results["missing_required"]:
                    st.write(f"- Learn and practise {skill}.")

            if results["missing_preferred"]:
                st.write(
                    "After addressing required gaps, work on these "
                    "preferred skills:"
                )

                for skill in results["missing_preferred"]:
                    st.write(f"- Explore {skill}.")

            if (
                not results["missing_required"]
                and not results["missing_preferred"]
            ):
                st.success(
                    "All detected job-description skills matched "
                    "the resume keywords."
                )

            st.divider()
            st.subheader("Personalized Learning Roadmap")

            roadmap_skills = (
                [
                    (skill, "required")
                    for skill in results["missing_required"]
                ]
                + [
                    (skill, "preferred")
                    for skill in results["missing_preferred"]
                ]
            )

            if roadmap_skills:
                for skill, category in roadmap_skills:
                    show_roadmap(skill, category)
            else:
                st.write("No learning gaps were detected.")

            with st.expander("Skills detected in your resume"):
                if resume_skills:
                    for skill in resume_skills:
                        st.write(f"- {skill}")
                else:
                    st.write("No known skills were detected.")

            with st.expander("How the score is calculated"):
                st.write(
                    "Required skills contribute 70% of the score and "
                    "preferred skills contribute 30% when both categories "
                    "are present. If only one category exists, its score "
                    "is normalized to 100% of the available weight."
                )
                st.write(
                    "The score is based on detected keywords, not a "
                    "judgment of your actual ability. Only include skills "
                    "you can genuinely explain or demonstrate in an interview."
                )