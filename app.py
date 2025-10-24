import streamlit as st
import json
import re
import os

st.set_page_config(page_title="FinTech Readiness Assistant", page_icon="💼")

# Load resource mapping data
json_path = os.path.join(os.path.dirname(__file__), "resource_mapping.json")

with open(json_path, "r", encoding="utf-8") as f:
    resource_data = json.load(f)

st.title("💼 QDB FinTech Readiness Assistant")
st.write("Upload your business plan to receive QDB program recommendations and a readiness score.")

uploaded_file = st.file_uploader("📎 Upload your business plan (TXT or PDF)", type=["txt"])

# Mock compliance rulebook
compliance_rules = {
    "Licensing Strategy": 0.3,
    "Corporate Structure": 0.2,
    "QCB Engagement": 0.5,
    "AML Policy Drafting": 0.4,
    "Transaction Monitoring": 0.3,
    "FATF Compliance": 0.3
}

def extract_keywords(text):
    keywords = []
    for rule in compliance_rules.keys():
        if re.search(rule.lower(), text.lower()):
            keywords.append(rule)
    return keywords

if uploaded_file:
    text = uploaded_file.read().decode("utf-8", errors="ignore")
    st.write("### 📄 Extracted Text Preview:")
    st.text(text[:500])

    keywords = extract_keywords(text)
    st.write("#### Detected Focus Areas:", ", ".join(keywords) if keywords else "None")

    # Match programs
    recommendations = []
    for program in resource_data["qdb_programs"]:
        if any(focus in program["focus_areas"] for focus in keywords):
            recommendations.append(program)

    if recommendations:
        st.write("### 🏛️ Recommended QDB Programs:")
        for rec in recommendations:
            st.markdown(f"**{rec['program_name']}** — Focus: {', '.join(rec['focus_areas'])}")
    else:
        st.warning("No direct match found. Try rephrasing your business plan focus areas.")

    score = sum(compliance_rules.get(k, 0) for k in keywords)
    readiness = round(score * 100, 2)
    st.metric("Regulatory Readiness Score", f"{readiness}/100")

st.divider()
st.caption("Prototype built by Duha — FinTech AI Readiness Assistant (Hackathon Edition)")
