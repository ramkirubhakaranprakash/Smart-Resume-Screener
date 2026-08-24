import streamlit as st
import json
import os
import re
import html

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Resume Screener",
    page_icon="📄",
    layout="wide"
)

DATA_FILE = "candidates.json"


# ============================================================
# SKILLS DATABASE
# ============================================================

SKILLS = {
    "Python": [r"\bpython\b"],
    "Java": [r"\bjava\b"],
    "C": [r"(?<![+#])\bc(?![+#])\b"],
    "C++": [r"\bc\+\+\b"],
    "C#": [r"\bc#\b", r"\bc sharp\b"],
    "SQL": [
        r"\bsql\b",
        r"\bmysql\b",
        r"\bpostgresql\b",
        r"\bpostgres\b",
        r"\boracle sql\b"
    ],
    "Git": [r"\bgit\b"],
    "GitHub": [r"\bgithub\b"],
    "AWS": [
        r"\baws\b",
        r"\bamazon web services\b"
    ],
    "Machine Learning": [
        r"\bmachine learning\b",
        r"\bml\b"
    ],
    "Deep Learning": [r"\bdeep learning\b"],
    "Artificial Intelligence": [
        r"\bartificial intelligence\b",
        r"\bai\b"
    ],
    "Data Science": [r"\bdata science\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "PyTorch": [
        r"\bpytorch\b",
        r"\btorch\b"
    ],
    "TensorFlow": [r"\btensorflow\b"],
    "OpenCV": [
        r"\bopencv\b",
        r"\bcomputer vision\b"
    ],
    "Scikit-learn": [
        r"\bscikit[- ]?learn\b",
        r"\bsklearn\b"
    ],
    "YOLO": [r"\byolo\b"],
    "YOLOv8": [r"\byolov8\b"],
    "HTML": [r"\bhtml\b"],
    "CSS": [r"\bcss\b"],
    "JavaScript": [
        r"\bjavascript\b",
        r"\bjs\b"
    ],
    "React": [r"\breact\b"],
    "Node.js": [r"\bnode\.?js\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b"],
    "Linux": [r"\blinux\b"],
    "DBMS": [
        r"\bdbms\b",
        r"\bdatabase management\b"
    ],
    "MongoDB": [
        r"\bmongodb\b",
        r"\bmongo db\b"
    ],
    "Oracle": [r"\boracle\b"],
    "Tableau": [r"\btableau\b"],
    "Power BI": [
        r"\bpower bi\b",
        r"\bpowerbi\b"
    ],
    "Excel": [
        r"\bexcel\b",
        r"\bmicrosoft excel\b"
    ],
    "R": [r"(?<![a-zA-Z])r(?![a-zA-Z])"]
}


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
    color: #f1f5f9;
}

[data-testid="stHeader"] {
    background-color: #0e1117;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

.hero-box {
    border: 1px solid #344052;
    border-radius: 18px;
    padding: 35px;
    margin-bottom: 40px;
    background: #161e29;
}

.hero-title-custom {
    font-size: 3.2rem;
    font-weight: 800;
    margin-bottom: 18px;
}

.hero-subtitle-custom {
    font-size: 1.3rem;
    color: #cbd5e1;
    margin-bottom: 20px;
}

.hero-small-custom {
    color: #94a3b8;
    font-size: 1rem;
}

.section-title {
    font-size: 2.2rem;
    font-weight: 750;
    margin-bottom: 5px;
}

.section-subtitle {
    color: #94a3b8;
    font-size: 1.05rem;
    margin-bottom: 20px;
}

.skill-tag {
    display: inline-block;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 10px 17px;
    margin: 5px;
    background-color: #121821;
    color: #dbeafe;
    font-size: 16px;
}

.match-tag {
    display: inline-block;
    border: 1px solid #166534;
    border-radius: 14px;
    padding: 9px 15px;
    margin: 5px;
    background-color: #102a1b;
    color: #86efac;
    font-size: 15px;
}

.missing-tag {
    display: inline-block;
    border: 1px solid #7f1d1d;
    border-radius: 14px;
    padding: 9px 15px;
    margin: 5px;
    background-color: #2a1517;
    color: #fca5a5;
    font-size: 15px;
}

.rank-title {
    font-size: 2rem;
    font-weight: 750;
    margin-bottom: 20px;
}

.candidate-name {
    font-size: 1.8rem;
    font-weight: 750;
    margin-bottom: 8px;
}

.email-text {
    color: #60a5fa;
    font-size: 1.05rem;
    margin-bottom: 18px;
}

.score-label {
    color: #94a3b8;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.score-value {
    font-size: 3.2rem;
    font-weight: 800;
    color: #e2e8f0;
    margin: 12px 0;
}

.candidate-id {
    color: #94a3b8;
    margin-top: 15px;
    font-size: 1rem;
}

.analysis-box {
    background: #161e29;
    border: 1px solid #344052;
    border-radius: 15px;
    padding: 20px;
    margin-top: 10px;
}

.found-box {
    background-color: #123826;
    border-radius: 12px;
    padding: 15px 20px;
    color: #86efac;
    margin: 15px 0 25px 0;
    font-size: 1.05rem;
}

.empty-box {
    background-color: #15263a;
    border-radius: 12px;
    padding: 20px;
    color: #93c5fd;
    margin-top: 15px;
}

div[data-testid="stFileUploader"] {
    border: 1px solid #344052;
    border-radius: 15px;
    padding: 15px;
    background-color: #18202c;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background-color: #2b303c !important;
    color: white !important;
    border: 1px solid #344052 !important;
    border-radius: 10px !important;
}

.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    min-height: 45px !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def load_candidates():

    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except Exception:
        return []


def save_candidates(candidates):

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(candidates, file, indent=4)


def delete_candidate(candidate_id):

    candidates = load_candidates()

    candidates = [
        candidate
        for candidate in candidates
        if candidate.get("id") != candidate_id
    ]

    save_candidates(candidates)


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(uploaded_file):

    try:
        uploaded_file.seek(0)

        reader = PdfReader(uploaded_file)

        pages = []

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                pages.append(page_text)

        return "\n".join(pages)

    except Exception as error:

        st.error(f"Could not read this PDF: {error}")

        return ""


# ============================================================
# EMAIL EXTRACTION
# ============================================================

def extract_email(text):

    pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'

    emails = re.findall(pattern, text)

    if emails:
        return emails[0]

    return "Not available"


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(text):

    if not text:
        return []

    found_skills = []

    normalized_text = re.sub(
        r"[\u200b\ufeff]",
        " ",
        text.lower()
    )

    for skill, patterns in SKILLS.items():

        for pattern in patterns:

            if re.search(
                pattern,
                normalized_text,
                flags=re.IGNORECASE
            ):
                found_skills.append(skill)
                break

    return sorted(
        list(set(found_skills)),
        key=str.lower
    )


# ============================================================
# PROFILE SCORE
# ============================================================

def calculate_profile_score(skills):

    if not skills:
        return 0.0

    max_skills = 12

    score = (
        len(set(skills))
        / max_skills
    ) * 100

    return round(
        min(score, 100.0),
        2
    )


# ============================================================
# JOB MATCH SCORE
# ============================================================

def calculate_job_match(
    candidate_skills,
    required_skills
):

    if not required_skills:

        return (
            calculate_profile_score(candidate_skills),
            [],
            []
        )

    candidate_set = {
        skill.lower()
        for skill in candidate_skills
    }

    matched_skills = [
        skill
        for skill in required_skills
        if skill.lower() in candidate_set
    ]

    missing_skills = [
        skill
        for skill in required_skills
        if skill.lower() not in candidate_set
    ]

    score = (
        len(matched_skills)
        / len(required_skills)
    ) * 100

    return (
        round(score, 2),
        matched_skills,
        missing_skills
    )


# ============================================================
# ORDINAL FUNCTION
# ============================================================

def get_ordinal(number):

    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {
            1: "st",
            2: "nd",
            3: "rd"
        }.get(number % 10, "th")

    return f"{number}{suffix}"


# ============================================================
# MATCH LABEL
# ============================================================

def get_match_label(score):

    if score >= 75:
        return "Excellent Match"

    elif score >= 50:
        return "Good Match"

    return "Needs Improvement"


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero-box">

<div class="hero-title-custom">
📄 Smart Resume Screener
</div>

<div class="hero-subtitle-custom">
Upload resumes, analyze candidate skills, compare them with job requirements,
and get intelligent recruiter insights.
</div>

<div class="hero-small-custom">
AI-powered candidate screening and job-specific ranking system
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# JOB REQUIREMENTS
# ============================================================

st.markdown(
    '<div class="section-title">💼 Job Requirements</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Paste a job description or enter the required technical skills for the role.'
    '</div>',
    unsafe_allow_html=True
)


job_description = st.text_area(
    "Job Description / Required Skills",

    placeholder=(
        "Example:\n\n"
        "Machine Learning Engineer\n\n"
        "Required Skills:\n"
        "Python\n"
        "Machine Learning\n"
        "SQL\n"
        "AWS\n"
        "Docker\n"
        "Git"
    ),

    height=200
)


required_skills = extract_skills(job_description)


if job_description.strip() and not required_skills:

    st.warning(
        "No supported technical skills were detected. "
        "Please include skills such as Python, Java, SQL, AWS, Docker, etc."
    )


if required_skills:

    st.markdown("### 🎯 Detected Required Skills")

    required_html = "".join(
        f'<span class="match-tag">{html.escape(skill)}</span>'
        for skill in required_skills
    )

    st.markdown(
        required_html,
        unsafe_allow_html=True
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# UPLOAD RESUME
# ============================================================

st.markdown(
    '<div class="section-title">📥 Upload Resume</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Upload a candidate resume in PDF format for automatic skill analysis.'
    '</div>',
    unsafe_allow_html=True
)


with st.container(border=True):

    col1, col2 = st.columns(2)

    with col1:

        uploaded_file = st.file_uploader(
            "Choose a resume PDF",
            type=["pdf"],
            accept_multiple_files=False
        )

    with col2:

        candidate_name = st.text_input(
            "Candidate Name",
            placeholder="Enter candidate name"
        )

    analyze_button = st.button(
        "🚀 Upload & Analyze Resume",
        type="primary"
    )


# ============================================================
# ANALYZE AND SAVE
# ============================================================

if analyze_button:

    if uploaded_file is None:

        st.error(
            "Please upload a PDF resume."
        )

    elif not candidate_name.strip():

        st.error(
            "Please enter the candidate name."
        )

    else:

        with st.spinner(
            "Analyzing resume..."
        ):

            resume_text = extract_pdf_text(
                uploaded_file
            )

            if not resume_text.strip():

                st.error(
                    "Could not extract text from this PDF. "
                    "Please upload a text-based PDF resume."
                )

            else:

                email = extract_email(
                    resume_text
                )

                skills = extract_skills(
                    resume_text
                )

                candidates = load_candidates()

                new_id = 1

                if candidates:

                    new_id = max(
                        candidate.get("id", 0)
                        for candidate in candidates
                    ) + 1

                new_candidate = {
                    "id": new_id,
                    "name": candidate_name.strip(),
                    "email": email,
                    "skills": skills,
                    "profile_score": calculate_profile_score(
                        skills
                    )
                }

                duplicate_index = None

                for index, existing in enumerate(
                    candidates
                ):

                    same_email = (
                        email != "Not available"
                        and existing.get(
                            "email",
                            ""
                        ).lower() == email.lower()
                    )

                    same_name = (
                        existing.get(
                            "name",
                            ""
                        ).strip().lower()
                        ==
                        candidate_name.strip().lower()
                    )

                    if same_email or same_name:

                        duplicate_index = index

                        new_candidate["id"] = existing.get(
                            "id",
                            new_id
                        )

                        break

                if duplicate_index is not None:

                    candidates[
                        duplicate_index
                    ] = new_candidate

                else:

                    candidates.append(
                        new_candidate
                    )

                save_candidates(
                    candidates
                )

                st.success(
                    f"Candidate "
                    f"'{candidate_name.strip()}' "
                    f"analyzed successfully!"
                )

                st.rerun()


# ============================================================
# RANKED CANDIDATES
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

st.divider()

st.markdown("<br>", unsafe_allow_html=True)


st.markdown(
    '<div class="section-title">🏆 Ranked Candidates</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Candidates are ranked based on the current job requirements.'
    '</div>',
    unsafe_allow_html=True
)


candidates = load_candidates()

ranked_candidates = []


for candidate in candidates:

    score, matched_skills, missing_skills = (
        calculate_job_match(
            candidate.get(
                "skills",
                []
            ),
            required_skills
        )
    )

    candidate_copy = candidate.copy()

    candidate_copy["score"] = score

    candidate_copy["matched_skills"] = (
        matched_skills
    )

    candidate_copy["missing_skills"] = (
        missing_skills
    )

    ranked_candidates.append(
        candidate_copy
    )


ranked_candidates = sorted(
    ranked_candidates,
    key=lambda candidate: candidate.get(
        "score",
        0
    ),
    reverse=True
)


# ============================================================
# SEARCH
# ============================================================

search_query = st.text_input(
    "🔍 Search candidates",
    placeholder="Search by candidate name or skill..."
)

search_text = search_query.lower().strip()

filtered_candidates = []


for candidate in ranked_candidates:

    name = candidate.get(
        "name",
        ""
    ).lower()

    skills_text = " ".join(
        candidate.get(
            "skills",
            []
        )
    ).lower()

    if (
        not search_text
        or search_text in name
        or search_text in skills_text
    ):

        filtered_candidates.append(
            candidate
        )


# ============================================================
# FOUND COUNT
# ============================================================

st.markdown(
    f"""
    <div class="found-box">
        ✓ {len(filtered_candidates)} candidate(s) found
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DISPLAY CANDIDATES
# ============================================================

if not filtered_candidates:

    st.markdown(
        """
        <div class="empty-box">
        No candidates found.
        </div>
        """,
        unsafe_allow_html=True
    )


else:

    medals = [
        "🥇",
        "🥈",
        "🥉"
    ]

    for rank, candidate in enumerate(
        filtered_candidates,
        start=1
    ):

        if rank <= 3:

            medal = medals[
                rank - 1
            ]

        else:

            medal = "🏅"


        score = float(
            candidate.get(
                "score",
                0
            )
        )

        match_label = get_match_label(
            score
        )


        # ====================================================
        # RANK
        # ====================================================

        st.markdown(
            f"""
            <div class="rank-title">
                {medal} {get_ordinal(rank)} Place
            </div>
            """,
            unsafe_allow_html=True
        )


        left_col, right_col = st.columns(
            [2, 1]
        )


        # ====================================================
        # LEFT SIDE
        # ====================================================

        with left_col:

            candidate_name_safe = html.escape(
                str(
                    candidate.get(
                        "name",
                        "Unknown Candidate"
                    )
                )
            )

            st.markdown(
                f"""
                <div class="candidate-name">
                    {candidate_name_safe}
                </div>
                """,
                unsafe_allow_html=True
            )


            email = candidate.get(
                "email",
                "Not available"
            )

            st.markdown(
                f"""
                <div class="email-text">
                    📧 {html.escape(str(email))}
                </div>
                """,
                unsafe_allow_html=True
            )


            st.markdown(
                '<div class="score-label">'
                'DETECTED TECHNICAL SKILLS'
                '</div>',
                unsafe_allow_html=True
            )


            candidate_skills = candidate.get(
                "skills",
                []
            )


            if candidate_skills:

                skills_html = "".join(
                    f'<span class="skill-tag">'
                    f'{html.escape(str(skill))}'
                    f'</span>'

                    for skill in candidate_skills
                )

                st.markdown(
                    skills_html,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    '<span class="skill-tag">'
                    'No skills detected'
                    '</span>',
                    unsafe_allow_html=True
                )


            # ================================================
            # MATCHED AND MISSING SKILLS
            # ================================================

            if required_skills:


                st.markdown(
                    "<br>",
                    unsafe_allow_html=True
                )


                st.markdown(
                    '<div class="score-label">'
                    '✓ MATCHED JOB SKILLS'
                    '</div>',
                    unsafe_allow_html=True
                )


                matched_skills = candidate.get(
                    "matched_skills",
                    []
                )


                if matched_skills:

                    matched_html = "".join(
                        f'<span class="match-tag">'
                        f'{html.escape(str(skill))}'
                        f'</span>'

                        for skill in matched_skills
                    )

                    st.markdown(
                        matched_html,
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        '<span class="missing-tag">'
                        'No required skills matched'
                        '</span>',
                        unsafe_allow_html=True
                    )


                st.markdown(
                    "<br>",
                    unsafe_allow_html=True
                )


                st.markdown(
                    '<div class="score-label">'
                    '✗ MISSING JOB SKILLS'
                    '</div>',
                    unsafe_allow_html=True
                )


                missing_skills = candidate.get(
                    "missing_skills",
                    []
                )


                if missing_skills:

                    missing_html = "".join(
                        f'<span class="missing-tag">'
                        f'{html.escape(str(skill))}'
                        f'</span>'

                        for skill in missing_skills
                    )

                    st.markdown(
                        missing_html,
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        '<span class="match-tag">'
                        'No missing required skills'
                        '</span>',
                        unsafe_allow_html=True
                    )


            # ================================================
            # RECRUITER ANALYSIS
            # IMPORTANT:
            # Native Streamlit components are used here.
            # NO HTML code will be printed on screen.
            # ================================================

            st.markdown("<br>")

            st.subheader("🤖 Recruiter Analysis")

            with st.container(border=True):

                if required_skills:

                    matched = candidate.get(
                        "matched_skills",
                        []
                    )

                    missing = candidate.get(
                        "missing_skills",
                        []
                    )

                    if score >= 75:

                        recommendation = (
                            "Strong candidate for this role. "
                            "The candidate matches most of the required "
                            "technical skills and should be considered for "
                            "shortlisting."
                        )

                    elif score >= 50:

                        recommendation = (
                            "Moderate fit for this role. "
                            "The candidate has relevant skills but is missing "
                            "some important job requirements."
                        )

                    else:

                        recommendation = (
                            "The candidate currently has a low match with "
                            "the job requirements. Consider only if the "
                            "missing skills can be developed or are not "
                            "critical for the role."
                        )


                    st.markdown(
                        "### Recommendation"
                    )

                    st.write(
                        recommendation
                    )


                    st.markdown(
                        "### 💪 Candidate Strengths"
                    )


                    if matched:

                        for skill in matched:

                            st.write(
                                f"• Matches required skill: **{skill}**"
                            )

                    else:

                        st.write(
                            "• No required technical skills "
                            "were matched."
                        )


                    st.markdown(
                        "### 🚀 Improvement Suggestions"
                    )


                    if missing:

                        for skill in missing:

                            st.write(
                                f"• Consider strengthening **{skill}**"
                            )

                    else:

                        st.write(
                            "• No missing skills detected "
                            "for the current job requirements."
                        )


                else:

                    st.markdown(
                        "### Recommendation"
                    )

                    st.write(
                        "Add a job description or required skills to "
                        "generate a job-specific recruiter analysis."
                    )


                    st.markdown(
                        "### 💪 Candidate Strengths"
                    )

                    if candidate_skills:

                        st.write(
                            "• Technical skills have been "
                            "automatically extracted from the resume."
                        )

                        st.write(
                            f"• {len(candidate_skills)} "
                            "technical skills detected."
                        )

                    else:

                        st.write(
                            "• No supported technical skills were "
                            "detected."
                        )


                    st.markdown(
                        "### 🚀 Improvement Suggestions"
                    )

                    st.write(
                        "• Add job requirements to generate a "
                        "detailed job-specific analysis."
                    )


        # ====================================================
        # RIGHT SIDE
        # ====================================================

        with right_col:


            if required_skills:

                score_label = "JOB MATCH SCORE"

            else:

                score_label = "PROFILE SCORE"


            st.markdown(
                f"""
                <div class="score-label">
                    {score_label}
                </div>
                """,
                unsafe_allow_html=True
            )


            st.markdown(
                f"""
                <div class="score-value">
                    {score:.2f}%
                </div>
                """,
                unsafe_allow_html=True
            )


            st.progress(
                min(
                    max(
                        score / 100,
                        0.0
                    ),
                    1.0
                )
            )


            if score >= 75:

                st.success(
                    f"● {match_label}"
                )

            elif score >= 50:

                st.info(
                    f"● {match_label}"
                )

            else:

                st.warning(
                    f"● {match_label}"
                )


            if required_skills:

                matched_count = len(
                    candidate.get(
                        "matched_skills",
                        []
                    )
                )

                st.caption(
                    f"{matched_count} of "
                    f"{len(required_skills)} "
                    f"required skills matched"
                )


            st.markdown(
                f"""
                <div class="candidate-id">
                    Candidate ID:
                    {candidate.get("id")}
                </div>
                """,
                unsafe_allow_html=True
            )


            if st.button(
                "🗑 Delete Candidate",
                key=f"delete_{candidate.get('id')}",
                use_container_width=True
            ):

                delete_candidate(
                    candidate.get("id")
                )

                st.rerun()


        st.divider()