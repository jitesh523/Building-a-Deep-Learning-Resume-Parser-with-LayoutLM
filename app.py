import logging
import os
import shutil
import csv
from io import StringIO
import streamlit as st
from utils.pdf_utils import extract_text, extract_links_and_contact
from utils.embedding_utils import get_relevant_resume_content
from utils.llm_utils import analyze_resume, parse_llm_scores
from config import GEMINI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("Resume Matcher 1.0")
st.markdown("Upload resumes and paste a job description to rank candidates.")

temp_dir = "temp_resumes"

def get_job_sections(jd_text):
    try:
        logger.info("Splitting job description")
        lines = jd_text.lower().split('\n')
        education_lines = [line for line in lines if any(word in line for word in ["education", "bachelor", "degree"])]
        experience_lines = [line for line in lines if any(word in line for word in ["experience", "years"])]
        skills_lines = [line for line in lines if any(word in line for word in ["skills", "proficiency", "tools"])]
        return {
            'education': "\n".join(education_lines).strip() or jd_text,
            'experience': "\n".join(experience_lines).strip() or jd_text,
            'skills': "\n".join(skills_lines).strip() or jd_text
        }
    except Exception as e:
        logger.error(f"Error splitting job description: {str(e)}")
        return {'education': jd_text, 'experience': jd_text, 'skills': jd_text}

if 'results' not in st.session_state:
    st.session_state['results'] = []

uploaded_files = st.file_uploader("Upload Resumes (PDFs)", type="pdf", accept_multiple_files=True)
job_description = st.text_area("Paste Job Description")

if st.button("Analyze Resumes"):
    if not uploaded_files or not job_description.strip():
        st.warning("Please upload at least one resume and a job description.")
        logger.error("Missing resumes or job description")
        st.stop()

    logger.info("Starting resume analysis")
    job_sections = get_job_sections(job_description)

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    results = []
    for idx, uploaded_file in enumerate(uploaded_files):
        file_name = uploaded_file.name
        resume_path = os.path.join(temp_dir, f"resume_{idx}.pdf")
        
        with open(resume_path, "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner(f"Processing {file_name}..."):
            resume_text = extract_text(resume_path)
            if not resume_text:
                st.warning(f"Failed to extract text from {file_name}")
                logger.error(f"Failed to extract text from {file_name}")
                continue

            contact_info = extract_links_and_contact(resume_text)
            relevant_content = get_relevant_resume_content(resume_text, job_description)
            if not relevant_content:
                st.warning(f"No relevant content found in {file_name}. Using full resume text.")
                logger.error(f"No relevant content for {file_name}")
                relevant_content = resume_text[:2000]

            ai_report = analyze_resume(relevant_content, job_sections, GEMINI_API_KEY)
            scores = parse_llm_scores(ai_report)

            results.append({
                'name': file_name,
                'overall_score': scores['overall'],
                'section_scores': {
                    'education': scores['education'],
                    'experience': scores['experience'],
                    'skills': scores['skills']
                },
                'report': ai_report,
                'contact': contact_info
            })

    results = sorted(results, key=lambda x: x['overall_score'], reverse=True)
    st.session_state['results'] = results
    logger.info("Resume analysis completed")

    st.success("Analysis Complete")
    st.subheader("Resume Rankings")
    ranking_data = [
        {
            'Rank': i + 1,
            'Resume': res['name'],
            'Overall Match (%)': res['overall_score'],
            'Education Match (%)': res['section_scores']['education'],
            'Experience Match (%)': res['section_scores']['experience'],
            'Skills Match (%)': res['section_scores']['skills']
        }
        for i, res in enumerate(results)
    ]
    st.table(ranking_data)

    for i, res in enumerate(results):
        st.markdown(f"### {i+1}. {res['name']}")
        try:
            report = res['report']
            overall = report.split("Education Match:")[0].strip()
            education = report.split("Education Match:")[1].split("Experience Match:")[0].strip()
            experience = report.split("Experience Match:")[1].split("Skills Match:")[0].strip()
            skills = report.split("Skills Match:")[1].split("Suggestions:")[0].strip()
            suggestions = report.split("Suggestions:")[1].strip()

            st.markdown("**Match Report:**")
            st.text(overall)
            st.markdown("**Education Match:**")
            st.text(education)
            st.markdown("**Experience Match:**")
            st.text(experience)
            st.markdown("**Skills Match:**")
            st.text(skills)
            st.markdown("**Suggestions:**")
            st.text(suggestions)
        except Exception as e:
            st.warning(f"Couldn't parse report for {res['name']}")
            st.text(res['report'])
            logger.error(f"Error parsing report for {res['name']}: {str(e)}")

if st.session_state.get('results') and st.button("Export to CSV"):
    logger.info("Exporting results to CSV")
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'Rank', 'Resume', 'Overall Match (%)', 'Education Match (%)',
        'Experience Match (%)', 'Skills Match (%)',
        'Email', 'Phone', 'LinkedIn', 'GitHub'
    ])
    writer.writeheader()
    for i, res in enumerate(st.session_state['results']):
        writer.writerow({
            'Rank': i + 1,
            'Resume': res['name'],
            'Overall Match (%)': res['overall_score'],
            'Education Match (%)': res['section_scores']['education'],
            'Experience Match (%)': res['section_scores']['experience'],
            'Skills Match (%)': res['section_scores']['skills'],
            'Email': ", ".join(res['contact'].get('email', [])),
            'Phone': ", ".join(res['contact'].get('phone', [])),
            'LinkedIn': ", ".join(res['contact'].get('linkedin', [])),
            'GitHub': ", ".join(res['contact'].get('github', []))
        })
    csv_data = output.getvalue()
    st.download_button(
        label="Download Results",
        data=csv_data,
        file_name="resume_rankings.csv",
        mime="text/csv"
    )

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
    logger.info("Cleaned up temp directory")