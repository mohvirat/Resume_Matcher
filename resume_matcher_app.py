# resume_matcher_app/app.py
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import docx
import os
import re

# -------------------- Helper Functions -------------------- #
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return " ".join([para.text for para in doc.paragraphs])

def parse_resume(file):
    if file.type == "application/pdf":
        return extract_text_from_pdf(file)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file)
    else:
        return ""

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
st.title("📄 Resume Matcher App")

st.subheader("Step 1: Paste Job Description")
jd_input = st.text_area("Enter or paste the Job Description below:")

st.subheader("Step 2: Input Essential and Preferred Skills")
essential_input = st.text_input("Essential Skills (comma-separated)")
preferred_input = st.text_input("Preferred Skills (comma-separated)")

st.subheader("Step 3: Upload Resumes (PDF/DOCX)")
resume_files = st.file_uploader("Upload multiple resumes", type=["pdf", "docx"], accept_multiple_files=True)

st.subheader("Step 4: Input Years of Experience")
skill_experience_map = {}

if essential_input or preferred_input:
    all_skills = list(set([s.strip() for s in (essential_input + "," + preferred_input).split(",") if s.strip()]))
    for skill in all_skills:
        years = st.number_input(f"Years of experience in '{skill}'", min_value=0, max_value=50, value=0, step=1)
        skill_experience_map[skill] = years

# -------------------- Processing -------------------- #
if st.button("Match Resumes") and resume_files:
    essential_skills = [s.strip() for s in essential_input.split(',') if s.strip()]
    preferred_skills = [s.strip() for s in preferred_input.split(',') if s.strip()]

    results = []

    for file in resume_files:
        resume_text = parse_resume(file)
        match_score = calculate_match(resume_text, essential_skills, preferred_skills, skill_experience_map)
        results.append({"Candidate": file.name, "Match %": match_score, "Color": colorize(match_score)})

    df = pd.DataFrame(results)

    def highlight_row(row):
        return [f'color: {row.Color}'] * len(row)

    st.subheader("📊 Match Results")
    st.dataframe(df.style.apply(highlight_row, axis=1).hide_columns(["Color"]))

    st.success("Matching completed!")

# -------------------- End -------------------- #

# -------------------- requirements.txt -------------------- #
# Save this as requirements.txt in the same folder as app.py

# streamlit and its dependencies
streamlit

# resume parsing and document support
pandas
PyMuPDF
python-docx

# -------------------- .streamlit/config.toml -------------------- #
# Optional UI settings (create a .streamlit folder and save this as config.toml)
[server]
headless = true
enableCORS = false

[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

# -------------------- README.md -------------------- #
# Save this as README.md in the root folder

# 📄 Resume Matcher App
This web app allows recruiters to match multiple resumes to a job description using essential and preferred skills, with weighting and experience adjustment.

## Features
- Upload multiple PDF/DOCX resumes
- Input essential and preferred skills
- Provide years of experience per skill
- See match % and color-coded scores

## How to Run
1. Clone the repo:
```bash
git clone https://github.com/yourusername/resume-matcher-app
cd resume-matcher-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run app.py
```

Or deploy directly on [Streamlit Cloud](https://streamlit.io/cloud).
