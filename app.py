import streamlit as st
import json
import os
import re

# --- Page Setup ---
st.set_page_config(page_title="FinTech Readiness Assistant", page_icon="💼")
st.title("💼 QDB FinTech Readiness Assistant")
st.write(
    "Upload your startup documents to receive regulatory gap analysis and QDB program recommendations."
)

# --- Load Resource Mapping Data ---
# Streamlit Cloud uses the repo root as working directory
RESOURCE_FILE = "resource_mapping.json"

if not os.path.exists(RESOURCE_FILE):
    st.error(f"Resource mapping file not found: {RESOURCE_FILE}")
    st.stop()

with open(RESOURCE_FILE, "r", encoding="utf-8") as f:
    resource_data = json.load(f)

# --- Mock Compliance Rules (from QCB docs) ---
# Ideally, parse these from the qcb_*.md files
compliance_rules = {
    "Licensing Strategy": 0.3,
    "Corporate Structure": 0.2,
    "QCB Engagement": 0.5,
    "AML Policy Drafting": 0.4,
    "Transaction Monitoring": 0.3,
    "FATF Compliance": 0.3,
    "Data Residency": 0.5,
    "Compliance Officer": 0.4,
    "Capital Requirement": 0.5,
    "Source of Funds": 0.3,
}

# --- Helper Function: Keyword Extraction ---
def extract_keywords(text):
    detected = []
    for rule in compliance_rules.keys():
        if re.search(rule.lower(), text.lower()):
            detected.append(rule)
    return detected

# --- File Upload Section ---
uploaded_file = st.file_uploader(
    "📎 Upload your startup document (TXT or PDF)", type=["txt"]
)

if uploaded_file:
    # Read uploaded text file
    text = uploaded_file.read().decode("utf-8", errors="ignore")
    st.write("### 📄 Document Preview:")
    st.text(text[:500])

    # Extract compliance keywords
    keywords = extract_keywords(text)
    st.write(
        "#### Detected Focus Areas:", ", ".join(keywords) if keywords else "None"
    )

    # --- Match Programs ---
    recommendations = []
    for program in resource_data.get("qdb_programs", []):
        if any(focus in program["focus_areas"] for focus in keywords):
            recommendations.append(program)

    if recommendations:
        st.write("### 🏛️ Recommended QDB Programs:")
        for rec in recommendations:
            st.markdown(
                f"**{rec['program_name']}** — Focus: {', '.join(rec['focus_areas'])} — Eligibility: {rec['eligibility']}"
            )
    else:
        st.warning("No direct match found. Try rephrasing your startup document focus areas.")

    # --- Match Experts ---
    experts = []
    for expert in resource_data.get("compliance_experts", []):
        if any(keyword in expert["specialization"] for keyword in keywords):
            experts.append(expert)

    if experts:
        st.write("### 👩‍💼 Recommended Compliance Experts:")
        for exp in experts:
            st.markdown(f"**{exp['name']}** — Specialization: {exp['specialization']} — Contact: {exp['contact']}")

    # --- Compute Readiness Score ---
    score = sum(compliance_rules.get(k, 0) for k in keywords)
    readiness = round(score * 100, 2)
    st.metric("Regulatory Readiness Score", f"{readiness}/100")

