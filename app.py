import streamlit as st
import os
import json
import re
from io import BytesIO

# Install dependencies: pip install python-docx PyPDF2
from docx import Document
import PyPDF2

# --- Page Config ---
st.set_page_config(page_title="FinTech Readiness Assistant", page_icon="💼")

# --- Load Resource Mapping Data ---
json_path = os.path.join(os.path.dirname(__file__), "resource_mapping.json")
with open(json_path, "r", encoding="utf-8") as f:
    resource_data = json.load(f)

# --- Mock Compliance Rules ---
compliance_rules = {
    "Licensing Strategy": 0.3,
    "Corporate Structure": 0.2,
    "QCB Engagement": 0.5,
    "AML Policy Drafting": 0.4,
    "Transaction Monitoring": 0.3,
    "FATF Compliance": 0.3,
    "Data Residency": 0.5,
    "Compliance Officer": 0.4,
    "Capital Requirement": 0.3,
    "Source of Funds": 0.3,
}

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "📎 Upload your startup document", type=["txt", "pdf", "docx"]
)

def extract_text(file):
    """Extract text based on file type."""
    filename = file.name.lower()

    if filename.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")
    
    elif filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    elif filename.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    
    else:
        return None

def extract_keywords(text):
    """Detect which compliance rules are mentioned in the text."""
    keywords = []
    for rule in compliance_rules.keys():
        if re.search(rule.lower(), text.lower()):
            keywords.append(rule)
    return keywords

# --- Main Logic ---
if uploaded_file:
    text = extract_text(uploaded_file)
    if not text:
        st.error("Unsupported file type.")
    else:
        st.write("### 📄 Document Preview")
        st.text(text[:500])

        # Extract keywords (focus areas)
        keywords = extract_keywords(text)
        st.write("#### Detected Focus Areas:", ", ".join(keywords) if keywords else "None")

        # Match programs based on focus areas
        program_recommendations = []
        for program in resource_data.get("qdb_programs", []):
            if any(focus in program["focus_areas"] for focus in keywords):
                program_recommendations.append(program)

        # Match experts if gaps exist
        expert_recommendations = []
        for expert in resource_data.get("compliance_experts", []):
            if any(rule.lower() in expert["specialization"].lower() for rule in keywords):
                expert_recommendations.append(expert)

        # Display program recommendations
        if program_recommendations:
            st.write("### 🏛️ Recommended QDB Programs:")
            for rec in program_recommendations:
                st.markdown(f"**{rec['program_name']}** — Focus: {', '.join(rec['focus_areas'])}")
        else:
            st.warning("No direct program match found. Try rephrasing your focus areas.")

        # Display expert recommendations
        if expert_recommendations:
            st.write("### 👩‍💼 Recommended Compliance Experts:")
            for expert in expert_recommendations:
                st.markdown(f"**{expert['name']}** — Specialization: {expert['specialization']} — Contact: {expert['contact']}")
        else:
            st.info("No expert recommendation found based on detected gaps.")

        # Calculate readiness score
        score = sum(compliance_rules.get(k, 0) for k in keywords)
        readiness = round(score * 100, 2)
        st.metric("Regulatory Readiness Score", f"{readiness}/100")

