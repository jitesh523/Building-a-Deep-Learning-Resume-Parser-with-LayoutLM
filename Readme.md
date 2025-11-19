# AI Resume Matcher

An AI-powered web application that analyzes how well a resume matches a job description and ranks candidates based on multiple criteria.

> Repository: `jitesh523/Building-a-Deep-Learning-Resume-Parser-with-LayoutLM`  
> Implementation: semantic embeddings + Google Gemini (LLM) + Streamlit.

---

## 🔍 Overview

This app helps recruiters and candidates quickly understand how well a resume fits a specific job posting.  
You can upload multiple resume PDFs, paste a job description, and get:

- An **overall match score**
- Separate scores for **education**, **experience**, and **skills**
- **Actionable suggestions** to improve each resume
- Extracted **contact details** (email, phone, LinkedIn, GitHub)
- An optional **CSV export** with all results

---

## ✨ Features

- **Multi‑resume support**  
  Upload several PDF resumes and compare them against a single job description.

- **Smart relevance filtering**  
  Uses semantic embeddings and cosine similarity to select only the most relevant parts of each resume before sending them to the LLM.

- **Section‑wise scoring**  
  The job description is broken down into:
  - Education
  - Experience
  - Skills  
  Each section receives its own 0–100 score.

- **LLM‑based feedback**  
  A Google Gemini model (via LangChain) generates:
  - Overall Match: `<0–100>%` + one‑line summary  
  - Education Match: `<0–100>%` + one‑line summary  
  - Experience Match: `<0–100>%` + one‑line summary  
  - Skills Match: `<0–100>%` + one‑line summary  
  - 2–3 short improvement suggestions

- **Contact info extraction**  
  From each resume, the app extracts:
  - Email addresses  
  - Phone numbers (with support for Indian formats)  
  - LinkedIn profiles  
  - GitHub profiles  

- **Recruiter‑friendly UI**  
  Built with Streamlit:
  - Ranked table of all resumes
  - Detailed per‑candidate report
  - One‑click CSV export

---

## 🧠 Approach

To keep the system both accurate and cost‑efficient:

1. **Text extraction (PDF → text)**  
   - Uses `PyPDFLoader` to read PDF resumes.
   - Normalizes text (lowercasing, whitespace cleanup).

2. **Job description structuring**  
   - Splits the JD into three logical sections:
     - Education
     - Experience
     - Skills  
   - Falls back gracefully if those keywords are missing.

3. **Semantic relevance using embeddings**  
   - Splits each resume into chunks with `RecursiveCharacterTextSplitter`.
   - Generates embeddings with  
     `sentence-transformers/all-MiniLM-L6-v2`.
   - Computes cosine similarity between each chunk and the job description context.
   - Keeps only the top‑K most relevant chunks (or those above a similarity threshold).

4. **LLM analysis (Google Gemini)**  
   - Combines:
     - Structured JD sections
     - Selected relevant resume chunks
   - Sends them to Gemini via LangChain’s `ChatGoogleGenerativeAI`.
   - Receives a structured, human‑readable report.

5. **Score parsing & ranking**  
   - Regex‑parses the LLM output into numeric scores.
   - Sorts all candidates by overall match in descending order.

---

## 🛠 Tech Stack

- **Language**: Python 3.10+
- **Web Framework**: Streamlit
- **LLM / AI**: Google Gemini via `langchain-google-genai`
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` via `HuggingFaceEmbeddings`
- **PDF Processing**: `PyPDFLoader` (LangChain community)
- **Similarity**: Cosine similarity (`sklearn`)

---

## 📂 Project Structure

```text
/
├── app.py                 # Main Streamlit application
├── sample_data/           # Example resumes (PDF)
├── utils/
│   ├── embedding_utils.py # Resume relevance / embedding logic
│   ├── llm_utils.py       # LLM calls and score parsing
│   └── pdf_utils.py       # PDF text + contact & link extraction
├── config.py              # Environment configuration (API keys)
├── requirements.txt       # Python dependencies
├── Readme.md              # Project documentation
└── .gitignore             # Ignored files