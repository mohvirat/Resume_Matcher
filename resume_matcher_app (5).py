# Resume Match and Ranking Script (No Streamlit)

import pandas as pd
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os
import difflib

# Set OpenAI API Key (ensure it's set in your environment)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ Missing OpenAI API Key. Please set OPENAI_API_KEY in environment variables.")
openai.api_key = api_key

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------

def extract_text_from_pdf(uploaded_file_path):
    with open(uploaded_file_path, "rb") as f:
        pdf_reader = PdfReader(f)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

def calculate_similarity(text, jd_text):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([jd_text, text])
    return cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100

def generate_ai_summary(text):
    prompt = f"""
    Analyze the following resume content:

    {text[:4000]}

    Provide a summary with:
    - Key strengths
    - Weaknesses
    - Technologies used
    - Project experience
    Keep it clear and concise.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional technical recruiter."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"AI Summary failed: {e}"

def fuzzy_match(term, text, threshold=0.6):
    words = text.split()
    matches = [word for word in words if difflib.SequenceMatcher(None, word.lower(), term.lower()).ratio() >= threshold]
    return bool(matches)

def evaluate_skills(resume_text, essential_skills, preferred_skills):
    all_skills = essential_skills + preferred_skills
    resume_lower = resume_text.lower()
    skill_results = {}
    for skill in all_skills:
        match_found = fuzzy_match(skill, resume_lower)
        skill_results[skill] = "🟢" if match_found else "🔴"
    essential_match = sum(skill_results[k] == "🟢" for k in essential_skills)
    preferred_match = sum(skill_results[k] == "🟢" for k in preferred_skills)

    essential_score = (essential_match / len(essential_skills)) * 70 if essential_skills else 0
    preferred_score = (preferred_match / len(preferred_skills)) * 30 if preferred_skills else 0
    weighted_score = round(essential_score + preferred_score, 2)

    return skill_results, weighted_score, essential_match, preferred_match

def color_match_level(score):
    if score >= 80:
        return "🟢 High"
    elif score >= 60:
        return "🟡 Medium"
    else:
        return "🔴 Low"

# ---------------------------
# MAIN SCRIPT
# ---------------------------

def process_resumes(jd_text, resume_paths, essential_skills, preferred_skills):
    results = []

    for resume_path in resume_paths:
        try:
            text = extract_text_from_pdf(resume_path)
            ai_summary = generate_ai_summary(text)
            skill_map, weighted_score, essential_hit, preferred_hit = evaluate_skills(
                text, essential_skills, preferred_skills)

            results.append({
                "Candidate": os.path.basename(resume_path),
                "Skill Match %": weighted_score,
                "Match Level": color_match_level(weighted_score),
                "Essential Skills": f"{essential_hit}/{len(essential_skills)}",
                "Preferred Skills": f"{preferred_hit}/{len(preferred_skills)}",
                "Skills Table": skill_map,
                "AI Summary": ai_summary
            })
        except Exception as e:
            print(f"Error processing {resume_path}: {e}")

    return pd.DataFrame(results)

# Example usage (replace with actual paths and inputs)
if __name__ == "__main__":
    job_description = "Your job description text here."
    resume_files = ["resume1.pdf", "resume2.pdf"]
    essential = ["Python", "SQL"]
    preferred = ["Docker", "Kubernetes"]

    df = process_resumes(job_description, resume_files, essential, preferred)
    print(df[["Candidate", "Skill Match %", "Essential Skills", "Preferred Skills", "Match Level"]])
