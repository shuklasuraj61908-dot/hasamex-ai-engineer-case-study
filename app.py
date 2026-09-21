import os,re
from pathlib import Path
import streamlit as st
try:
    from openai import OpenAI
except Exception:
    OpenAI=None

st.set_page_config(page_title='Expert Call Analyzer',page_icon='🤖',layout='wide')
DATA=Path(__file__).parent/'data'
QUESTIONS=[
'How would you describe current adoption of robotic surgery systems in Europe?',
'What are the main barriers to adoption?',
'How important are hospital budgets and ROI in purchasing decisions?',
'How important are surgeon training and clinical outcomes?',
'What adoption trend do you expect over the next 3–5 years?',
'What is the typical hospital decision-making timeline for purchasing a robotic system?']
META={'France':('Dr. Jean Martin','Head of Urology'),'Germany':('Anna Keller','Former Hospital Procurement Director'),'UK':('Dr. Emily Carter','Consultant Urologist')}
ALIASES={1:['adoption','growing','uneven','concentrated'],2:['barrier','cost','funding','capital','training'],3:['roi','economic','budget','finance','cost'],4:['training','surgeon','clinical','outcome','staff','utilisation'],5:['outlook','growth','accelerate','gradual','annually'],6:['purchase','timeline','months','decision','capital cycle','procurement']}

def parse(text,market):
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    entries=[]; ts='00:00'; speaker=None; buf=[]
    for line in lines:
        if re.fullmatch(r'\d{2}:\d{2}',line):
            if speaker and buf: entries.append({'timestamp':ts,'speaker':speaker,'text':' '.join(buf),'market':market})
            ts=line; speaker=None; buf=[]; continue
        if ':' in line and speaker is None:
            speaker,body=line.split(':',1); buf=[body.strip()]
        elif speaker: buf.append(line)
    if speaker and buf: entries.append({'timestamp':ts,'speaker':speaker,'text':' '.join(buf),'market':market})
    qa=[]
    for i,e in enumerate(entries):
        if e['speaker'].lower()=='interviewer':
            for nxt in entries[i+1:i+3]:
                if nxt['speaker'].lower()!='interviewer':
                    qa.append({'question':e['text'],'answer':nxt['text'],'timestamp':nxt['timestamp'],'market':market}); break
    return {'entries':entries,'qa':qa,'name':META[market][0],'role':META[market][1]}

def load():
    files={'France':'Transcript_1_France.txt','Germany':'Transcript_2_Germany.txt''UK': 'Transcript_3_UK.txt'}
    return {m:parse((DATA/f).read_text(encoding='utf-8'),m) for m,f in files.items() if(DATA/f).exists()
def best(doc,n):
    scored=[]
    for item in doc['qa']:
        h=(item['question']+' '+item['answer']).lower()(DATA/f).exists(); score=sum(h.count(x) for x in ALIASES[n]); scored.append((score,item))
    return sorted(scored,key=lambda x:x[0],reverse=True)[0][1]

def retrieve(docs,q,k=6):
    terms=re.findall(r'[a-zA-Z]{3,}',q.lower()); out=[]
    for d in docs.values():
        for e in d['entries']:
            score=sum(e['text'].lower().count(t) for t in terms)
            if score: out.append((score,e))
    out.sort(key=lambda x:x[0],reverse=True); return [e for _,e in out[:k]]

def llm(prompt):
    key=st.session_state.get('key') or os.getenv('OPENAI_API_KEY')
    if not key or OpenAI is None:return ''
    c=OpenAI(api_key=key); model=os.getenv('OPENAI_MODEL','gpt-4o-mini')
    r=c.chat.completions.create(model=model,temperature=0,messages=[
      {'role':'system','content':'Use ONLY supplied transcript evidence. Never invent facts. Cite substantive claims with [MARKET | TIMESTAMP]. If evidence is insufficient, say so.'},
      {'role':'user','content':prompt}])
    return r.choices[0].message.content

docs=load()
st.title('🤖 Expert Call Analyzer')
st.caption('Hasamex AI Engineer technical case study — evidence-grounded demo')
with st.sidebar:
    st.header('Controls')
    st.session_state['key']=st.text_input('Optional OpenAI API key',type='password')
    st.caption('Core transcript/evidence features work without an API key. AI synthesis and Ask AI use the key.')

T1,T2,T3,T4=st.tabs(['Expert Analysis','Themes & Differences','Ask AI','Transcript Viewer'])
with T1:
    market=st.selectbox('Expert / market',list(docs))
    d=docs[market]; st.write(f"**{d['name']}** — {d['role']} — {market}")
    n=st.selectbox('Interview question',range(1,7),format_func=lambda x:f'{x}. {QUESTIONS[x-1]}')
    m=best(d,n)
    st.markdown('### Evidence-based answer'); st.write(m['answer'])
    st.markdown('### Exact supporting quote'); st.success('“'+m['answer']+'”')
    st.markdown(f"**Source:** {market} transcript — **{m['timestamp']}**")
    if st.button('AI-summarize this answer'):
        prompt=f"Question: {QUESTIONS[n-1]}\nEvidence: [SOURCE={market} | TIMESTAMP={m['timestamp']}] {m['answer']}\nWrite 2–4 concise sentences using only this evidence and cite the source."
        r=llm(prompt); st.write(r or 'No API key configured; the evidence-based answer above is available.')
with T2:
    st.subheader('Cross-expert comparison')
    st.markdown('### Common themes')
    for x in ['Adoption is described as growing/increasing in all three markets.','Economics, cost or funding are important considerations.','Training and sufficient utilisation/procedure volume recur as operational issues.','All three interviews describe continued growth rather than declining adoption.']: st.write('• '+x)
    st.markdown('### Differences / disagreements')
    for x in ['France emphasizes capital-budget approval and ROI/utilisation.','Germany emphasizes procurement economics, total cost of ownership and competing capital priorities.','The UK describes economics and clinical strategy as balanced and emphasizes training capacity.','The interview timelines are France 6–12 months, Germany 9–18 months, and UK around 6–9 months when funding is already available.']: st.write('• '+x)
with T3:
    q=st.text_area('Ask a question across all transcripts',placeholder='Example: What are the main barriers to adoption?')
    if st.button('Ask') and q.strip():
        hits=retrieve(docs,q)
        evidence='\n\n'.join(f"[SOURCE={e['market']} | TIMESTAMP={e['timestamp']} | SPEAKER={e['speaker']}] {e['text']}" for e in hits)
        r=llm(f'User question: {q}\n\nTranscript evidence:\n{evidence}\n\nAnswer only from this evidence. Cite claims with [MARKET | TIMESTAMP].')
        st.markdown('### Answer'); st.write(r or 'Evidence-only answer:')
        if not r:
            for e in hits: st.write(f"- **{e['market']} | {e['timestamp']}** — {e['text']}")
        st.markdown('### Retrieved sources')
        for e in hits: st.write(f"- **{e['market']} | {e['timestamp']}** — {e['text']}")
with T4:
    market=st.selectbox('Transcript',list(docs),key='viewer');
    for e in docs[market]['entries']:
        st.markdown(f"**{e['timestamp']} — {e['speaker']}**"); st.write(e['text']); st.divider()
st.caption('Important claims should remain traceable to transcript evidence; insufficient evidence should be stated explicitly.')
