import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_relevant_resume_content(resume_text, job_desc, chunk_size=1000, chunk_overlap=200, top_k=5, similarity_threshold=0.5):
    try:
        logger.info("Extracting relevant resume content")
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_text(resume_text)
        if not chunks:
            logger.error("No chunks created from resume text")
            return ""

        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

        # combining job sections with existing jd for more weight to important sections.
        job_sections = {
            'education': [line for line in job_desc.lower().split('\n') if any(word in line for word in ["education", "bachelor", "degree"])],
            'experience': [line for line in job_desc.lower().split('\n') if any(word in line for word in ["experience", "years"])],
            'skills': [line for line in job_desc.lower().split('\n') if any(word in line for word in ["skills", "proficiency", "tools"])]
        }
        job_context = job_desc + "\n" + "\n".join(sum(job_sections.values(), []))

        # embedding
        job_emb = embeddings.embed_query(job_context)
        chunk_embs = [embeddings.embed_query(chunk) for chunk in chunks]

        similarities = cosine_similarity([job_emb], chunk_embs)[0]

        # Select chunks above threshold or top-k
        relevant_indices = [i for i, score in enumerate(similarities) if score >= similarity_threshold]
        if not relevant_indices:
            # fallback
            relevant_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]

        relevant_indices = relevant_indices[:top_k]
        relevant_chunks = [chunks[i] for i in relevant_indices]
        logger.info(f"Selected {len(relevant_chunks)} relevant chunks")
        return "\n".join(relevant_chunks)
    except Exception as e:
        logger.error(f"Error in get_relevant_resume_content: {str(e)}")
        return ""