# Resume Matcher

A web application that analyzes how well a resume matches a job description using AI.

Created by <your name>.

## What It Does

- Upload one or multiple resume PDFs
- Paste a job description
- Get match scores for education, experience, and skills
- Receive concrete improvement suggestions

## Features

- **PDF Processing** – Extracts text from resume PDFs
- **Smart Matching** – Uses embeddings + LLMs to compare resume content with job requirements
- **Detailed Analysis** – Separate scores for education, experience, and skills
- **Improvement Tips** – Short, actionable suggestions to improve the resume
- **Contact Extraction** – Pulls email, phone, LinkedIn, and GitHub from the resume

## Approach

I optimized the app to be both accurate and cost‑efficient:

1. **Token Reduction** – The job description is split into key sections (education, experience, skills) so the LLM gets focused context.
2. **Semantic Filtering** – I use embeddings + cosine similarity to select only the most relevant chunks from each resume instead of sending the entire document.
3. **Weighted Matching** – The original JD is combined with the extracted sections to give more weight to important requirements.
4. **LLM Feedback** – The LLM returns:
   - Overall Match (0–100) with a one‑line summary
   - Education Match (0–100)
   - Experience Match (0–100)
   - Skills Match (0–100)
   - 2–3 short suggestions
5. **Recruiter‑Friendly Output** – Results are shown in a sortable table in Streamlit and can be exported to CSV.

---

## Tech Stack

- **Frontend / UI** – Streamlit
- **AI / LLM** – Google Gemini via LangChain
- **Embeddings** – `sentence-transformers/all-MiniLM-L6-v2`
- **PDF Processing** – LangChain `PyPDFLoader`
- **Language** – Python 3.10+

---

## Setup

### Prerequisites

- Python 3.10+
- Google API Key (for Gemini)

### Installation

1. **Clone the repository**

   ```bash
   git clone [https://github.com/<your-github-username>/Resume-Matcher.git](https://github.com/<your-github-username>/Resume-Matcher.git)
   cd Resume-Matcher