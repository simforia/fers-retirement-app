import streamlit as st
from datetime import datetime
from fpdf import FPDF
import os

# 🔍 Page Tracking for Metrics (Session ID)
st.session_state.setdefault("visits", 0)
st.session_state.visits += 1

# 📊 Increase Global Font Size
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-size: 18px !important;
        }
    </style>
""", unsafe_allow_html=True)

# 🔼 Title Centered Without Logo
st.markdown("""
<div style="text-align: center;">
    <h2 style="margin-bottom: 0;">Simforia Intelligence Group</h2>
    <p style='font-size: 18px; margin-top: 0;'><em>Retirement Optimization Toolkit – DRP / VERA / TSP Strategy Suite</em></p>
    <small><strong>Important Notice: For Informational Purposes Only</strong><br>
</div>
""", unsafe_allow_html=True)

# 📘 Instructions
with st.expander("ℹ️ How to Use This Tool"):
    st.markdown("""
    1. Enter your current age and total federal service.
    2. Select whether you are participating in DRP.
    3. Review your eligibility and key deadlines.
    4. Use the GPT link at the bottom for deeper TSP insights.
    5. Generate a DRP participation letter.
    """)

# ✅ Required Inputs for Eligibility Logic
current_age = st.number_input("Current Age", min_value=18, max_value=80)
years_service = st.number_input("Years of Federal Service", min_value=0, max_value=50)
drp_participation = st.selectbox("Participating in DRP?", ["", "Yes", "No"])
vsip_offer = st.number_input("VSIP Offer ($, optional)", min_value=0)
high3_salary = st.number_input("High-3 Average Salary ($)", min_value=0)

include_survivor = st.checkbox("Include Survivor Benefit Election")
survivor_reduction = 0.10 if include_survivor else 0.0
survivor_percentage = 0.5 if include_survivor else 0.0

cola_rate = st.slider("COLA Estimate (Annual % Starting at Age 62)", min_value=0.0, max_value=5.0, value=2.0, step=0.1)

# 📊 Retirement Benefits Calculation
st.markdown("### 📘 Estimated FERS Retirement Benefits")

# TSP Inputs
tsp_balance = st.number_input("Current TSP Balance ($)", min_value=0)
tsp_contribution_pct = st.slider("TSP Contribution (% of Salary)", 0, 100, 5)

# Constants
fers_multiplier = 0.01
social_security_estimate = 1800  # est. monthly SS at 62
tsp_return_rate = 0.06
retirement_age = current_age
years_until_62 = max(0, 62 - current_age)
tsp_contribution_annual = high3_salary * (tsp_contribution_pct / 100)

# FERS Pension
base_fers = high3_salary * fers_multiplier * years_service
fers_annuity = base_fers * (1 - survivor_reduction)

# SRS
if current_age < 62 and years_service >= 20:
    srs = (years_service / 40) * (social_security_estimate * 12)
    srs_text = f"${srs:,.2f} annually until age 62"
else:
    srs = 0
    srs_text = "Not eligible or over 62"

# TSP Growth
future_tsp = tsp_balance
for _ in range(int(years_until_62)):
    future_tsp = (future_tsp + tsp_contribution_annual) * (1 + tsp_return_rate)

# Output
st.write(f"**FERS Pension (Annual Estimate):** ${fers_annuity:,.2f}")
st.write(f"**Special Retirement Supplement (SRS):** {srs_text}")
st.write(f"**Projected TSP at Age 62:** ${future_tsp:,.2f}")

# 🔘️ DRP Auto-Fill Letter Generator
with st.expander("✍️ Generate DRP Participation Letter"):
    user_name = st.text_input("Your Full Name")
    user_series = st.text_input("Position Title / Series / Grade")
    user_component = st.text_input("Your Duty Station or Component")

    if st.button("🔕 Generate DRP Letter"):
        letter_text = f"""
Subject: Formal Election of DRP and VERA Participation

Dear [HR Representative],

In accordance with the Department of Defense guidance issued April 1, 2025, and my verified eligibility for both the Deferred Resignation Program (DRP) and Voluntary Early Retirement Authority (VERA), I am formally submitting my intent to:

- Elect participation in the DoD DRP, beginning administrative leave on or after May 1, 2025, and
- Retire under the VERA authority, with an effective retirement date of September 30, 2025.

My current Position Description (PD#: {user_series}) explicitly confirms that I am not designated as mission-critical or emergency-essential, and I meet the service and age criteria for VERA ({current_age} years of age with {years_service} years of federal service).

The DoD memo explicitly states that VERA may be elected in conjunction with or independent of DRP, and that exemptions must be rare and justified under 10 U.S.C. §129a with higher-level concurrence. I have seen no documentation exempting my position, nor have I received any such notice.

I respectfully request written confirmation that my election of VERA + DRP is accepted, with my retirement date established as September 30, 2025 in accordance with the program rules.

Thank you for your timely response and support. Please consider this message an official election of both authorities unless instructed otherwise.

Respectfully,

{user_name}
{user_component}
        """
        st.code(letter_text)
        st.download_button("🔕 Download Letter as TXT", data=letter_text, file_name="drp_request_letter.txt")

# 🔗 GPT Link for TSP / DRP / VERA Q&A
st.markdown("---")
st.markdown("### 💬 Have Questions About TSP, DRP, or VERA?")
st.markdown("[🧠 Ask Simforia’s TSP Advisor GPT — Comprehensive TSP Strategy and Projections](https://chat.openai.com/g/g-67eea2244d2c819189bee5201afec0bc-tsp-advisor-by-simforia-intellegence-group) →")

# 🗘️ Provide Contact Information for Feedback
st.markdown("### 📧 Contact Simforia Intelligence Group")
st.markdown("""
If you have any questions or feedback regarding the tool, please reach out to our team securely. 
<form action="https://formspree.io/f/mzzejjkk" method="POST">
  <label>Your message:<br><textarea name="message"></textarea></label><br>
  <label>Your email (optional, for response):<br><input type="email" name="email"></label><br>
  <button type="submit">Send Feedback</button>
</form>
""", unsafe_allow_html=True)

# ⚠️ Legal Disclaimer
st.markdown("""
---
<small><strong>Important Notice: For Informational Purposes Only</strong><br>
This app is intended to provide general information and estimation tools to assist federal employees in exploring early retirement options under the Federal Employees Retirement System (FERS), including programs such as Voluntary Early Retirement Authority (VERA), Voluntary Separation Incentive Pay (VSIP), and the Deferred Retirement Program (DRP).<br><br>
While we strive to ensure accuracy, all projections, simulations, and financial analyses provided by this app are estimates only and should not be interpreted as official retirement guidance or a guarantee of future benefits. The calculations do not account for all variables, including changes to federal policy, tax laws, agency determinations, or individual circumstances.<br><br>
This app is not affiliated with the U.S. Office of Personnel Management (OPM), the Department of Defense, or any federal agency. Users should consult with a certified financial advisor, HR specialist, or official retirement counselor before making any retirement-related decisions.<br><br>
By using this app, you agree that the creators of the app are not responsible for any actions taken based on its output.</small>
""", unsafe_allow_html=True)
