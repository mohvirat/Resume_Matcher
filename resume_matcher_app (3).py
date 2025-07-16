# resume_matcher_app/app.py
# NOTE: This simplified version removes all external Python module dependencies
# and works entirely in standard browser-safe environments (no file parsing or pandas)

import streamlit as st

# -------------------- Helper Functions -------------------- #
def calculate_match(resume_text, essential_skills, preferred_skills, skill_experience_map):
    resume_text_lower = resume_text.lower()
    total_essential = len(essential_skills)
    total_preferred = len(preferred_skills)

    essential_score = 0
    preferred_score = 0

    for skill in essential_skills:
        if skill.lower() in resume_text_lower:
            weight = 1 + 0.1 * skill_experience_map.get(skill, 0)
            essential_score += weight

    for skill in preferred_skills:
        if skill.lower() in resume_text_lower:
            weight = 1 + 0.1 * skill_experience_map.get(skill, 0)
            preferred_score += weight

    max_essential_score = total_essential * 2
    max_preferred_score = total_preferred * 2

    essential_percent = (essential_score / max_essential_score * 100) if total_essential else 0
    preferred_percent = (preferred_score / max_preferred_score * 100) if total_preferred else 0

    total_score = (0.7 * essential_percent + 0.3 * preferred_percent)
    return round(total_score, 2)

def colorize(score):
    if score > 80:
        return 'green'
    elif score > 60:
        return 'orange'
    else:
        return 'red'

# -------------------- Streamlit UI -------------------- #
st.title("📄 Resume Matcher App (No External Dependencies)")

st.subheader("Step 1: Paste Job Description")
jd_input = st.text_area("Enter or paste the Job Description below:")

st.subheader("Step 2: Input Essential and Preferred Skills")
essential_input = st.text_input("Essential Skills (comma-separated)")
preferred_input = st.text_input("Preferred Skills (comma-separated)")

st.subheader("Step 3: Paste Resume Texts")
num_resumes = st.number_input("How many resumes do you want to compare?", min_value=1, max_value=10, value=1)
resume_texts = []
for i in range(num_resumes):
    resume_text = st.text_area(f"Paste Resume #{i+1} Text")
    resume_texts.append(resume_text)

st.subheader("Step 4: Input Years of Experience")
skill_experience_map = {}

if essential_input or preferred_input:
    all_skills = list(set([s.strip() for s in (essential_input + "," + preferred_input).split(",") if s.strip()]))
    for skill in all_skills:
        years = st.number_input(f"Years of experience in '{skill}'", min_value=0, max_value=50, value=0, step=1)
        skill_experience_map[skill] = years

# -------------------- Processing -------------------- #
if st.button("Match Resumes"):
    essential_skills = [s.strip() for s in essential_input.split(',') if s.strip()]
    preferred_skills = [s.strip() for s in preferred_input.split(',') if s.strip()]

    st.subheader("📊 Match Results")
    for i, text in enumerate(resume_texts):
        match_score = calculate_match(text, essential_skills, preferred_skills, skill_experience_map)
        color = colorize(match_score)
        st.markdown(f"**Resume #{i+1}** - Match: <span style='color:{color}'>{match_score}%</span>", unsafe_allow_html=True)

# -------------------- End -------------------- #

# ✅ This version does NOT require any external modules (like pandas, fitz, docx)
# It uses only Streamlit and native Python features.
# Resume content is pasted manually instead of uploading files.
