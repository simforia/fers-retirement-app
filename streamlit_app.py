# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import urllib.parse
import openai
import io
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tempfile
import requests

# Optional: Replace with your own OpenAI key if needed
openai.api_key = st.secrets.get("openai_api_key", "sk-REPLACE_WITH_YOUR_KEY")

# --- GPT Response Helper ---
def get_gpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error fetching GPT response: {e}"

# --- FERS Strategy Wizard UI ---
st.title("🧠 Simforia Prompt Wizards + GPT Strategy Tools")
st.markdown("## 🧓 FERS Strategy Wizard")

with st.expander("📋 Build Your FERS Retirement GPT Prompt"):
    st.markdown("#### 🔢 Step 1: Input Your Info")

    wizard_age = st.number_input("Current Age", min_value=18, max_value=80, value=53)
    wizard_service = st.number_input("Years of Federal Service", min_value=0, max_value=50, value=29)
    wizard_high3 = st.number_input("High-3 Salary ($)", min_value=0, value=110000)
    wizard_tsp_balance = st.number_input("Current TSP Balance ($)", min_value=0, value=1460000)
    wizard_tsp_contribution = st.slider("TSP Contribution Rate (%)", 0, 100, value=17)
    wizard_taxfree_income = st.number_input("Monthly Tax-Free Income ($)", min_value=0, value=3000)
    wizard_expenses = st.number_input("Monthly Living Expenses ($)", min_value=0, value=5000)
    wizard_mortgage_balance = st.number_input("Mortgage Balance ($)", min_value=0, value=18000)
    wizard_mortgage_payment = st.number_input("Mortgage Payment ($/mo)", min_value=0, value=3800)
    wizard_cash_savings = st.number_input("Cash Savings ($)", min_value=0, value=280000)
    wizard_spouse_income = st.number_input("Spouse Income ($/yr)", min_value=0, value=140000)

    gpt_prompt = f"""
I want to compare my retirement options under FERS. Use the info I provide to calculate pension income, TSP growth, cashflow, and breakeven age.

Age: {wizard_age}  
Years of service: {wizard_service}  
High-3 salary: ${wizard_high3:,.0f}  
TSP balance: ${wizard_tsp_balance:,.0f}  
TSP contribution: {wizard_tsp_contribution}%  
Tax-free income: ${wizard_taxfree_income}/mo  
Expenses: ${wizard_expenses}/mo  
Mortgage: ${wizard_mortgage_balance} left at ${wizard_mortgage_payment}/mo  
Cash savings: ${wizard_cash_savings}  
Spouse income: ${wizard_spouse_income}/yr

Compare retirement at 53, 55, 57.5, and 62.
Provide charts, analysis, and a strategic recommendation.
"""

    st.text_area("🧠 GPT Prompt", gpt_prompt, height=300)
    encoded_prompt = urllib.parse.quote(gpt_prompt)
    st.markdown(f"🚀 [Launch in GPT](https://chat.openai.com/g/g-67eea2244d2c819189bee5201afec0bc-tsp-advisor-by-simforia-intellegence-group?prompt={encoded_prompt})")

    if st.button("🤖 Run GPT Analysis Now"):
        response = get_gpt_response(gpt_prompt)
        st.markdown("#### ✅ GPT Response:")
        st.write(response)

# --- Contractor Strategy Wizard ---
st.markdown("## 🛠️ Contractor Launch Strategy Wizard")
with st.expander("🚀 Build a 1099 Transition Plan"):
    contractor_skill = st.text_input("What service will you offer as a contractor?", "federal compliance consulting")
    contractor_rate = st.number_input("Target Hourly Rate ($)", min_value=25, max_value=500, value=120)
    contractor_hours = st.number_input("Hours Per Week You Plan to Work", min_value=1, max_value=60, value=25)
    contractor_costs = st.number_input("Estimated Monthly Business Expenses ($)", min_value=0, value=1500)

    contractor_prompt = f"""
Help me evaluate a federal contractor launch strategy as a post-retirement path.

- Contractor Role: {contractor_skill}  
- Hourly Rate: ${contractor_rate}  
- Hours Per Week: {contractor_hours}  
- Monthly Overhead Costs: ${contractor_costs}

Estimate monthly profit, annual income, tax considerations, and how this compares to taking a regular retirement. Suggest basic startup steps and breakeven analysis.
"""

    st.text_area("💼 GPT Contractor Prompt", contractor_prompt, height=250)
    encoded_contractor_prompt = urllib.parse.quote(contractor_prompt)
    st.markdown(f"💬 [Launch Contractor Prompt in GPT](https://chat.openai.com/?prompt={encoded_contractor_prompt})")

    if st.button("💡 Run Contractor Strategy GPT Now"):
        result = get_gpt_response(contractor_prompt)
        st.markdown("#### ✅ GPT Strategy Output:")
        st.write(result)

# --- Job Explorer Helper ---
def fetch_remoteok_jobs(query):
    try:
        url = f"https://remoteok.com/api"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        data = response.json()
        results = [job for job in data if query.lower() in job.get("position", "").lower() or query.lower() in job.get("tags", [])]
        return results[:5]
    except Exception as e:
        return [{"position": f"Error fetching jobs: {e}", "company": "N/A", "location": "N/A", "url": ""}]

# --- Job Market Explorer ---

# --- Extended Job Filters ---
st.markdown("## 📈 Job Market Trends for Retirees")
with st.expander("🔍 Explore Current In-Demand Roles"):
    st.info("Live job data is powered by previewed API responses. Real-time API integrations with JobsPikr, BLS, or ZipRecruiter available.")

    region = st.selectbox("Select a Region", ["DC Metro", "Remote", "Texas", "California", "Florida"])
    skill = st.selectbox("Select an Industry or Skill", ["Cybersecurity", "Project Management", "Financial Coaching", "Health & VA Consulting", "Federal Compliance"])
    clearance = st.radio("Security Clearance Required?", ["No", "Preferred", "Required"])

    st.markdown(f"**🔎 Showing listings for: {skill} roles in {region} ({clearance})**")

    # --- Example real job board link based on inputs ---
    search_keywords = f"{skill} {region} {clearance}".replace(" ", "+")
    st.markdown(f"🌐 [Search on USAJobs.gov](https://www.usajobs.gov/Search/?k={search_keywords})")
    st.markdown(f"🌐 [Search on ZipRecruiter](https://www.ziprecruiter.com/candidate/search?search={search_keywords})")

    job_map = {
        "Cybersecurity": [
            {"title": "Cybersecurity Analyst", "location": region, "salary": "$120k avg, TS clearance preferred"},
            {"title": "InfoSec Consultant (1099)", "location": "Remote", "salary": "$105/hr (Contract)"},
        ],
        "Project Management": [
            {"title": "Federal Project Manager", "location": region, "salary": "$115k - $135k"},
            {"title": "Remote Agile PM", "location": "Remote", "salary": "$100k - $125k"},
        ],
        "Financial Coaching": [
            {"title": "Retirement Coach (Federal Focus)", "location": region, "salary": "$90/hr"},
        ],
        "Health & VA Consulting": [
            {"title": "VA Disability Consultant", "location": region, "salary": "$80k + bonuses"},
        ],
        "Federal Compliance": [
            {"title": "GovCon Compliance Advisor", "location": region, "salary": "$95k - $120k"},
        ],
    }

    job_data = job_map.get(skill, [])

    for job in job_data:
        st.markdown(f"**{job['title']}**
📍 {job['location']}  💵 {job['salary']}")

    st.caption("Real-time listings via live APIs coming soon. Want to sponsor deeper integrations? Contact Simforia Labs.")

st.markdown("## 🌐 Post-Retirement Job Market Explorer")
st.markdown("Explore live remote job listings tailored to your skills and transition goals.")

with st.expander("🔍 Search for Remote Job Roles by Keyword"):
    query = st.text_input("Enter job title or keyword (e.g. cybersecurity, project manager)", "cybersecurity")
    if query:
        jobs = fetch_remoteok_jobs(query)
        for job in jobs:
            st.markdown(f"**{job.get('position', 'Unknown')}** at **{job.get('company', 'Unknown')}**")
            st.markdown(f"📍 Location: {job.get('location', 'Remote')}")
            st.markdown(f"🔗 [Apply Now]({job.get('url', '#')})")
            st.markdown("---")

st.caption("Job data powered by RemoteOK. Contact Simforia for premium data feeds or regional filters.")
