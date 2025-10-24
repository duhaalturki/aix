import streamlit as st
import json
import re
import os

# Set page config
st.set_page_config(page_title="FinTech Readiness Assistant", page_icon="💼")

# Load resource mapping JSON
json_path = os.path.join(os.path.dirname(__file__), "resource_mapping.json")
with open(json_path, "r", encoding="utf-8") as f:
    resource_data = json.load(f)

# Load QCB rulebook files (mock)
qcb_rules = {}
rule_files = ["qcb_aml_data_protection_regulation.md",
              "qcb_fintech_licensing_pathways.md"]

for file_name in rule_files:
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            # Simple mapping: article title → text
            matches = re.findall(r"(Article\s[\d\.]+:[^\n]+)", f.read())
            for match in matches:
                qcb_rules[match] = match  # For prototype, we just store the article names

# Mock compliance weights for scoring
compliance_weights = {
    "Licensing Strategy": 0.3,
    "Corporate Structure": 0.2,
    "QCB Engagement": 0.5,
    "AML Policy Drafting": 0.4,
    "Transaction Monitoring": 0.3,
    "FATF Compliance": 0.3
}

# Streamlit UI
st.title("💼 QDB FinTech Readiness Assistant")
st.write("Upload your business plan to receive program recommendations and readiness score.")

uploaded_file = st.file_uploader("📎 Upload your business plan (TXT/MD)", type=["txt","md"])

def extract_keywords(text):
    keywords = []
    for rule in compliance_weights.keys():
        if re.search(rule.lower(), text.lower()):
            keywords.append(rule)
    return keywords

def detect_gaps(text):
    gaps = []
    if "AWS" in text or "Ireland" in text or "Singapore" in text:
        gaps.append("Data Residency Issue")
    if "compliance officer" not in text.lower():
        gaps.append("Missing Compliance Officer")
    if re.search(r"QAR\s?5,?000,?000", text):
        gaps.append("Capital Deficiency")
    return gaps

if uploaded_file:
    # Read text
    text = uploaded_file.read().decode("utf-8", errors="ignore")
    st.write("### 📄 Extracted Text Preview:")
    st.text(text[:500])

    # Extract focus areas & gaps
    keywords = extract_keywords(text)
    gaps = detect_gaps(text)

    st.write("#### Detected Focus Areas:", ", ".join(keywords) if keywords else "None")
    st.write("#### Detected Gaps:", ", ".join(gaps) if gaps else "None")

    # Recommend programs / experts
    recommendations = []
    for program in resource_data.get("qdb_programs", []):
        if any(focus in program["focus_areas"] for focus in keywords):
            recommendations.append(f"Program: {program['program_name']}")

    for expert in resource_data.get("compliance_experts", []):
        for gap in gaps:
            if gap == "Missing Compliance Officer" and "Compliance" in expert["specialization"]:
                recommendations.append(f"Expert: {expert['name']} ({expert['contact']})")

    if recommendations:
        st.write("### 🏛️ Recommendations:")
        for rec in recommendations:
            st.markdown(f"- {rec}")
    else:
        st.warning("No direct match found. Try rephrasing your business plan focus areas.")

    # Calculate readiness score
    score = sum(compliance_weights.get(k, 0) for k in keywords)
    readiness = round(score * 100, 2)
    st.metric("Regulatory Readiness Score", f"{readiness}/100")

st.divider()
st.caption("Prototype built by Duha — FinTech AI Readiness Assistant (Hackathon Edition)")

