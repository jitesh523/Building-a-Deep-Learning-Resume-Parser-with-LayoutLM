import logging
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_resume(resume_text, job_sections, api_key):
    try:
        logger.info("Starting LLM resume analysis")
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)
        if not llm:
            logger.error("Failed to initialize LLM")
            return "Analysis failed."

        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a recruiter. Analyze how well the resume matches the job description sections provided.
            Provide a structured response with:
            - Overall Match: <0-100>% - One sentence summary of overall fit.
            - Education Match: <0-100>% - One sentence summary.
            - Experience Match: <0-100>% - One sentence summary.
            - Skills Match: <0-100>% - One sentence summary.
            - Suggestions: 2-3 short improvement tips.
            Be concise and specific. Use the exact format above.
            """),
            ("user", """
            Job Description Sections:
            Education: {education}
            Experience: {experience}
            Skills: {skills}
            
            Resume: {resume}
            """)
        ])
        messages = prompt.format_messages(
            education=job_sections['education'],
            experience=job_sections['experience'],
            skills=job_sections['skills'],
            resume=resume_text
        )
        result = llm.invoke(messages)
        logger.info("LLM analysis completed")
        return result.content.strip()
    except Exception as e:
        logger.error(f"Error in analyze_resume: {str(e)}")
        return "Analysis error."

def parse_llm_scores(ai_report):
    try:
        logger.info("Parsing LLM report")
        overall = int(re.search(r"Overall Match:\s*(\d+)%", ai_report).group(1))
        education = int(re.search(r"Education Match:\s*(\d+)%", ai_report).group(1))
        experience = int(re.search(r"Experience Match:\s*(\d+)%", ai_report).group(1))
        skills = int(re.search(r"Skills Match:\s*(\d+)%", ai_report).group(1))
        return {
            'overall': overall,
            'education': education,
            'experience': experience,
            'skills': skills
        }
    except Exception as e:
        logger.error(f"Error parsing LLM scores: {str(e)}")
        return {
            'overall': 0,
            'education': 0,
            'experience': 0,
            'skills': 0
        }