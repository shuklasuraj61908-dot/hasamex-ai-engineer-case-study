import re
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="AI Expert Call Analyzer", layout="wide")

BASE = Path(__file__).parent
DATA = BASE / "data"

FILES = {
    "France": "Transcript_1_France.txt",
    "Germany": "Transcript_2_Germany.txt",
    "UK": "Transcript_3_UK.txt",
}

META = {
    "France": ("Dr. Jean Martin", "Head of Urology"),
    "Germany": ("Anna Keller", "Former Hospital Procurement Director"),
    "UK": ("Dr. Emily Carter", "Consultant Urologist"),
}

def parse_transcript(text, market):
    pattern = re.compile(
        r"(?m)^\s*(\d{2}:\d{2})\s*-\s*([^:]+):\s*(.*?)(?=^\s*\d{2}:\d{2}\s*-\s*|\Z)",
        re.S,
    )
    rows = []
    for timestamp, speaker, content in pattern.findall(text):
        rows.append(
            {
                "market": market,
                "timestamp": timestamp.strip(),
                "speaker": speaker.strip(),
                "text": " ".join(content.split()),
            }
        )
    return rows

@st.cache_data
def load_documents():
    docs = {}
    for market, filename in FILES.items():
        path = DATA / filename
        if path.exists():
            text = path.read_text(encoding="utf-8")
            docs[market] = parse_transcript(text, market)
    return docs

docs = load_documents()

def expert_answer(market, question):
    rows = docs.get(market, [])
    if not rows:
        return "Transcript not found.", "", ""

    terms = [x.lower() for x in re.findall(r"[a-zA-Z]{4,}", question)]
    scored = []
    for row in rows:
        score = sum(term in row["text"].lower() for term in terms)
        if row["speaker"].lower() != "interviewer":
            scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    best = [row for score, row in scored if score > 0][:3]
    if not best:
        best = [row for score, row in scored[:3]]

    quote = best[0]["text"] if best else ""
    timestamp = best[0]["timestamp"] if best else ""

    evidence = " ".join(row["text"] for row in best)
    return evidence, quote, timestamp

THEMES = [
    ("Adoption", "Adoption is increasing across all three markets, but access and speed vary by hospital."),
    ("Economics", "Cost, funding, ROI and utilisation are recurring factors in purchasing decisions."),
    ("Training", "Training surgeons and theatre staff is repeatedly identified as important for utilisation."),
    ("Growth", "All three experts expect continued growth, with different growth rates by market."),
]

st.title("🤖 AI Expert Call Analyzer")
st.caption("Hasamex AI Engineer Technical Case Study")

tabs = st.tabs(["Expert Analysis", "Themes & Differences", "Ask Questions", "Transcript Viewer"])

with tabs[0]:
    st.subheader("Expert Analysis")
    market = st.selectbox("Select market", list(FILES.keys()))
    questions = [
        "What are the main barriers to adoption?",
        "How important is ROI and economics?",
        "How important is training?",
        "What is the expected growth?",
        "How long does procurement usually take?",
    ]
    question = st.selectbox("Interview question", questions)
    answer, quote, timestamp = expert_answer(market, question)

    name, role = META[market]
    st.write(f"**{name}** — {role} — {market}")
    st.write("**Evidence-based answer:**", answer)
    if quote:
        st.write("**Exact quote:**", f'"{quote}"')
        st.write("**Timestamp:**", timestamp)

with tabs[1]:
    st.subheader("Common Themes")
    for title, text in THEMES:
        st.markdown(f"**{title}:** {text}")

    st.subheader("Market Differences")
    differences = {
        "France": "Strong emphasis on capital-budget approval, ROI, utilisation and payback.",
        "Germany": "Strong emphasis on total cost of ownership, procurement alignment and competing capital priorities.",
        "UK": "Balances economics with clinical strategy, outcomes, recruitment and training capacity.",
    }
    for market, text in differences.items():
        st.markdown(f"**{market}:** {text}")

with tabs[2]:
    st.subheader("Ask Questions Across Transcripts")
    query = st.text_input("Ask a question", placeholder="e.g. What are the main barriers to adoption?")
    if query:
        for market in FILES:
            answer, quote, timestamp = expert_answer(market, query)
            st.markdown(f"### {market}")
            st.write(answer)
            if quote:
                st.caption(f"Evidence: {timestamp} — {quote}")

with tabs[3]:
    st.subheader("Transcript Viewer")
    for market, rows in docs.items():
        with st.expander(market):
            for row in rows:
                st.markdown(
                    f"**{row['timestamp']} — {row['speaker']}:** {row['text']}"
                )

if not docs:
    st.error(
        "No transcripts were loaded. Make sure the three transcript files are inside a `data` folder."
    )
