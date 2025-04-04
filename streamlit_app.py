import streamlit as st
from datetime import datetime
from fpdf import FPDF
import os

# Track sessions
st.session_state.setdefault("visits", 0)
st.session_state.visits += 1

# Increase font
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-size: 18px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("""
<div style="text-align: center;">
    <h2 style="margin-bottom: 0;">Simforia Intelligence Group</h2>
    <p style='font-size: 18px; margin-top: 0;'><em>Retirement Optimization Toolkit – DRP / VERA / TSP Strategy Suite</em></p>
    <small><strong>Important Notice: For Informational Purposes Only</strong><br>
</div>
""", unsafe_allow_html=True)

# Instructions
with st.expander("ℹ️ How to Use This Tool"):
    st.markdown("""
    1. Enter your current age and federal service.
    2. Choose FEGLI and FEHB options.
    3. Adjust TSP and COLA.
    4. Set your planned retirement age.
    5. Review your projections and download a DRP letter.
    """)

# Inputs
current_age = st.number_input("Current Age", min_value=18, max_value=80)
years_service = st.number_input("Years of Federal Service", min_value=0, max_value=50)
retirement_age_input = st.number_input("Planned Retirement Age", min_value=current_age, max_value=80, value=62)
drp_participation = st.selectbox("Participating in DRP?", ["", "Yes", "No"])
vsip_offer = st.number_input("VSIP Offer ($, optional)", min_value=0)
high3_salary = st.number_input("High-3 Average Salary ($)", min_value=0)

# Survivor benefit logic
survivor_percent = st.selectbox("Survivor Annuity Election", ["None", "25%", "50%"])
if survivor_percent == "None":
    survivor_reduction = 0.0
    survivor_monthly_payment = 0
elif survivor_percent == "25%":
    survivor_reduction = 0.05
    survivor_monthly_payment = (high3_salary * 0.01 * years_service * 0.25) / 12
else:
    survivor_reduction = 0.10
    survivor_monthly_payment = (high3_salary * 0.01 * years_service * 0.5) / 12

cola_rate = st.slider("COLA Estimate (Annual % Starting at Age 62)", min_value=0.0, max_value=5.0, value=2.0, step=0.1)

# TSP Inputs
tsp_balance = st.number_input("Current TSP Balance ($)", min_value=0)
tsp_contribution_pct = st.slider("TSP Contribution (% of Salary)", 0, 100, 5)

# Pension + SRS + TSP Growth
fers_multiplier = 0.01
social_security_estimate = 1800
tsp_return_rate = 0.06
years_until_retirement = max(0, retirement_age_input - current_age)
tsp_contribution_annual = high3_salary * (tsp_contribution_pct / 100)
base_fers = high3_salary * fers_multiplier * years_service
fers_annuity = base_fers * (1 - survivor_reduction)

if current_age < 62 and years_service >= 20:
    srs = (years_service / 40) * (social_security_estimate * 12)
    srs_text = f"${srs:,.2f} annually until age 62"
else:
    srs = 0
    srs_text = "Not eligible or over 62"

# 🔄 Updated: TSP stops at retirement age
future_tsp = tsp_balance
for _ in range(int(years_until_retirement)):
    future_tsp = (future_tsp + tsp_contribution_annual) * (1 + tsp_return_rate)

# FEHB
fehb_option = st.selectbox("Will you retain FEHB (Health Insurance)?", ["No", "Yes - Self Only", "Yes - Self + Family"])
fehb_monthly_cost = {
    "No": 0,
    "Yes - Self Only": 200,
    "Yes - Self + Family": 500
}[fehb_option]

# FEGLI Option B
st.markdown("### 🧮 FEGLI Life Insurance Estimate")
retain_fegli = st.checkbox("Retain FEGLI Option B?")
fegli_coverage_multiplier = st.selectbox("FEGLI Option B Multiple of Salary", [0, 1, 2, 3, 4, 5], index=0)
def fegli_b_rate(age):
    return next(rate for age_max, rate in [
        (34, 0.02), (39, 0.03), (44, 0.06), (49, 0.09), (54, 0.16),
        (59, 0.36), (64, 0.86), (69, 1.86), (74, 3.56), (79, 6.28), (999, 8.64)
    ] if age <= age_max)

fegli_b_monthly = 0
if retain_fegli and fegli_coverage_multiplier > 0:
    coverage_units = (high3_salary / 1000) * fegli_coverage_multiplier
    fegli_b_monthly = round(coverage_units * fegli_b_rate(current_age), 2)

# FEGLI Option A
include_option_a = st.checkbox("Add FEGLI Option A ($10,000)?")
def fegli_a_rate(age):
    return next(rate for age_max, rate in [
        (34, 0.43), (39, 0.43), (44, 0.65), (49, 0.94), (54, 1.55),
        (59, 2.60), (64, 4.33), (69, 6.00), (74, 13.00), (79, 28.00), (999, 60.00)
    ] if age <= age_max)
fegli_a_monthly = fegli_a_rate(current_age) if include_option_a else 0

# FEGLI Option C
include_option_c = st.checkbox("Add FEGLI Option C (Spouse & Child)?")
option_c_multiple = st.selectbox("Option C Multiple (x $5k/$2.5k)", [0, 1, 2, 3, 4, 5], index=0) if include_option_c else 0
def fegli_c_rate(age):
    return next(rate for age_max, rate in [
        (34, 0.22), (39, 0.30), (44, 0.45), (49, 0.69), (54, 1.04),
        (59, 1.56), (64, 2.59), (69, 4.50), (74, 6.80), (79, 10.40), (999, 14.00)
    ] if age <= age_max)
fegli_c_monthly = fegli_c_rate(current_age) * option_c_multiple if include_option_c else 0

# Totals
fegli_total = fegli_b_monthly + fegli_a_monthly + fegli_c_monthly
monthly_insurance_cost = fehb_monthly_cost + fegli_total
monthly_fers_income = fers_annuity / 12
monthly_srs_income = srs / 12
monthly_net_income = monthly_fers_income + monthly_srs_income - monthly_insurance_cost

# Display Output
st.markdown("### 💸 Net Retirement Income Estimate")
st.write(f"**FERS Pension (Annual):** ${fers_annuity:,.2f}")
st.write(f"**Special Retirement Supplement:** {srs_text}")
st.write(f"**Projected TSP at Retirement (Age {retirement_age_input}):** ${future_tsp:,.2f}")
st.write(f"**Monthly Net Pension (After FEHB & FEGLI):** ${monthly_net_income:,.2f}")

# Breakdown
with st.expander("🧾 Insurance & Survivor Breakdown"):
    st.write(f"- **FEHB Premium:** ${fehb_monthly_cost:,.2f}")
    st.write(f"- **FEGLI Option B:** ${fegli_b_monthly:,.2f}")
    st.write(f"- **FEGLI Option A:** ${fegli_a_monthly:,.2f}")
    st.write(f"- **FEGLI Option C:** ${fegli_c_monthly:,.2f}")
    st.write(f"- **Total Insurance Cost:** ${monthly_insurance_cost:,.2f}")
    st.markdown("---")
    st.write(f"**Survivor Annuity Elected:** {survivor_percent}")
    if survivor_monthly_payment > 0:
        st.write(f"**Estimated Spouse Benefit (Monthly):** ${survivor_monthly_payment:,.2f}")

# DRP Letter Generator
with st.expander("✍️ Generate DRP Participation Letter"):
    user_name = st.text_input("Your Full Name")
    user_series = st.text_input("Position Description (PD#)")
    user_component = st.text_input("Your Duty Station or Component")

    if st.button("🔕 Generate DRP Letter"):
        letter_text = f"""
Subject: Formal Election of DRP and VERA Participation

Dear [HR Representative],

In accordance with the Department of Defense guidance issued April 1, 2025, and my verified eligibility for both the Deferred Resignation Program (DRP) and Voluntary Early Retirement Authority (VERA), I am formally submitting my intent to:

- Elect participation in the DoD DRP, beginning administrative leave on or after May 1, 2025, and
- Retire under the VERA authority, with an effective retirement date of September 30, 2025.

My current Position Description (PD#: {user_series}) explicitly confirms that I am not designated as mission-critical or emergency-essential, and I meet the service and age criteria for VERA ({current_age} years of age with {years_service} years of federal service).

Thank you for your timely response and support.

Respectfully,

{user_name}
{user_component}
        """
        st.code(letter_text)
        st.download_button("🔕 Download Letter as TXT", data=letter_text, file_name="drp_request_letter.txt")

# GPT Link
st.markdown("---")
st.markdown("### 💬 Have Questions About TSP, DRP, or VERA?")
st.markdown("[🧠 Ask Simforia’s TSP Advisor GPT](https://chat.openai.com/g/g-67eea2244d2c819189bee5201afec0bc-tsp-advisor-by-simforia-intellegence-group) →")

# Contact Form
st.markdown("### 📧 Contact Simforia Intelligence Group")
st.markdown("""
<form action="https://formspree.io/f/mzzejjkk" method="POST">
  <label>Your message:<br><textarea name="message"></textarea></label><br>
  <label>Your email (optional):<br><input type="email" name="email"></label><br>
  <button type="submit">Send Feedback</button>
</form>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
---
<small><strong>Important Notice: For Informational Purposes Only</strong><br>
This app helps federal employees explore early retirement under FERS, VERA, VSIP, and DRP. Estimates are not official guidance. Consult your HR office or a licensed advisor before making decisions.</small>
""", unsafe_allow_html=True)
