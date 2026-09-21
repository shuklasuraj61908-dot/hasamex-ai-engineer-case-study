# Demo Video Script

1. “Hi, I’m Suraj. I built this Expert Call Analyzer for the Hasamex AI Engineer case study. The goal is to analyze three expert-call transcripts while keeping answers traceable to the source.”

2. “In Expert Analysis, I select an expert and an interview-guide question. The app shows the evidence-based answer, the exact supporting quote and its timestamp.”

3. “Themes & Differences compares all three experts and keeps country-level differences visible.”

4. “In Ask AI, the user can ask a question across all transcripts. The system retrieves relevant evidence first; the optional LLM then synthesizes an answer from that evidence and cites market and timestamp.”

5. “The architecture is ingestion, timestamped evidence extraction, retrieval, optional LLM synthesis and Streamlit UI.”

6. “To reduce hallucinations, the model receives only retrieved transcript evidence and is instructed not to invent information. If evidence is insufficient, it should say so.”

7. “For 30 or more transcripts, I would replace keyword retrieval with embeddings and vector search, add metadata filters, reranking, caching and automated evaluation.”
