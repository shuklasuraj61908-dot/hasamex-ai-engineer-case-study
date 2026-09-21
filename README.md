# Hasamex AI Engineer — Expert Call Analyzer

Streamlit case-study app for analyzing the supplied France, Germany and UK expert-call transcripts.

## Features
- Six interview-guide questions for each expert
- Exact supporting quotes and timestamps
- Common themes and differences across experts
- Cross-transcript Ask AI
- Original transcript viewer
- Optional OpenAI synthesis grounded only in retrieved transcript evidence

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional AI mode
Set `OPENAI_API_KEY` and optionally `OPENAI_MODEL` before running. Never commit an API key to GitHub.

## Architecture
1. Ingest timestamped TXT transcripts.
2. Parse speaker/timestamp evidence records.
3. Match interview-guide questions to the relevant expert response.
4. Retrieve evidence for cross-transcript questions.
5. Optionally send only retrieved evidence to an LLM for synthesis.
6. Display answers with source market/timestamp.

## Hallucination controls
The model is instructed to use only supplied evidence, cite substantive claims, and say when evidence is insufficient. The original transcript viewer keeps the source auditable.

## Scaling to 30+
Use embeddings/vector search, stable document/chunk IDs, metadata filters, reranking, caching, batch ingestion, and automated evaluation for citation accuracy and faithfulness.
