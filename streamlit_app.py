# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# --- Setup ---
st.session_state.setdefault("visits", 0)
st.session_state.visits += 1

st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-size: 18px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center;">
    <h2 style="margin-bottom: 0;">Simforia Intelligence Group</h2>
    <p style='font-size: 18px; margin-top: 0;'><em>Retirement Optimization Toolkit – DRP / VERA / TSP Strategy Suite</em></p>
    <small><strong>Important Notice: For Informational Purposes Only</strong><br>
</div>
""", unsafe_allow_html=True)

# --- Instructions ---
with st.expander("ℹ️ How to Use This Tool"):
    st.markdown("""
    1. Enter your current age and total federal service.
    2. Input your TSP balance, high-3 salary, and contribution rate.
    3. Select your FEHB and FEGLI retirement coverage.
    4. View projected growth, income, and milestone ages.
    5. Compare monthly income streams.
    6. Visualize projected net worth including VA, TSP, FERS, SRS, FEHB, and DRP.
    """)

# --- Inputs ---
current_age = st.number_input("Current Age", min_value=18, max_value=80)
years_service = st.number_input("Years of Federal Service", min_value=0, max_value=50)
high3_salary = st.number_input("High-3 Average Salary ($)", min_value=0)
tsp_balance = st.number_input("Current TSP Balance ($)", min_value=0)
tsp_contribution_pct = st.slider("TSP Contribution (% of Salary)", 0, 100, 5)
tsp_contribution_annual = high3_salary * (tsp_contribution_pct / 100)

# --- FEHB & FEGLI Selection ---
fehb_plan = st.selectbox("FEHB Plan Type", ["None", "Self Only", "Self + One", "Family"])
fehb_costs = {"None": 0, "Self Only": 300, "Self + One": 550, "Family": 750}
fehb_premium = fehb_costs[fehb_plan]

fegli_option = st.selectbox("FEGLI Option", ["None", "Basic", "Basic + Option A", "Basic + Option B"])
fegli_costs = {"None": 0, "Basic": 50, "Basic + Option A": 70, "Basic + Option B": 90}
fegli_premium = fegli_costs[fegli_option]

monthly_expenses = st.number_input("Other Monthly Living Expenses ($)", min_value=0, value=3000)

# --- VA Disability ---
st.markdown("### VA Disability Compensation")
va_monthly = st.number_input("Monthly VA Disability Payment ($)", min_value=0, value=0)

# --- Disability Retirement Option ---
st.markdown("### Disability Retirement")
disability_retirement = st.checkbox("Apply FERS Disability Retirement Calculation Instead?")

# --- SRS Calculation ---
srs = (years_service / 40) * (1800 * 12) if current_age < 62 and years_service >= 20 else 0
srs_annual = srs if current_age < 62 else 0

# --- VERA / VSIP / DRP Options ---
st.markdown("### Separation Incentives")
vera_elected = st.checkbox("Elect Voluntary Early Retirement Authority (VERA)?")
vsip_amount = st.number_input("VSIP Offer Amount ($, if applicable)", min_value=0)
drp_elected = st.checkbox("Participating in DoD Deferred Resignation Program (DRP)?")

total_admin_leave_income = 0  # default if DRP not selected

if vera_elected:
    st.info("You have selected VERA: early retirement available with 20 years at age 50 or 25 years at any age.")
if drp_elected:
    st.info("You have elected the DRP. You may enter paid administrative leave beginning May 1, 2025.")
    st.warning("⚠️ You must separate from federal service by September 30, 2025 under DRP rules.")
if vsip_amount > 0:
    st.success(f"VSIP Lump Sum: ${vsip_amount:,.2f} will be added to your cash flow model.")

# --- DRP Admin Leave Simulation ---
if drp_elected:
    st.markdown("### DRP Administrative Leave Simulation")
    months_of_leave = st.slider("Months of Paid Leave Before Separation", 1, 5, 4)
    monthly_salary = high3_salary / 12
    total_admin_leave_income = months_of_leave * monthly_salary
    st.write(f"**Estimated Admin Leave Income (Before Final Separation):** ${total_admin_leave_income:,.2f}")

# --- Pension Calculations ---
fers_regular = high3_salary * 0.01 * years_service * 0.9
fers_disability = high3_salary * (0.6 if current_age < 62 else 0.4)

monthly_regular = round(fers_regular / 12, 2)
monthly_disability = round(fers_disability / 12, 2)

# --- Select which pension scenario to use ---
if disability_retirement:
    selected_fers_income = fers_disability
    selected_monthly_income = monthly_disability
    pension_label = "Disability Retirement"
else:
    selected_fers_income = fers_regular
    selected_monthly_income = monthly_regular
    pension_label = "Regular FERS Retirement"

# --- What-if Comparison ---
st.markdown("### 🧮 What-if Comparison: Disability vs. Regular Retirement")

comparison_data = {
    "Scenario": ["Regular FERS Retirement", "Disability Retirement"],
    "Annual Pension ($)": [fers_regular, fers_disability],
    "Monthly Pension ($)": [monthly_regular, monthly_disability],
    "SRS Eligible": ["Yes" if srs > 0 else "No"] * 2,
    "VA Monthly Added ($)": [va_monthly] * 2,
    "FEHB/FEGLI Annual Cost ($)": [fehb_premium * 12 + fegli_premium * 12] * 2
}
comp_df = pd.DataFrame(comparison_data)
comp_df = comp_df.style.format({
    "Annual Pension ($)": "${:,.2f}",
    "Monthly Pension ($)": "${:,.2f}",
    "VA Monthly Added ($)": "${:,.2f}",
    "FEHB/FEGLI Annual Cost ($)": "${:,.2f}"
})
st.dataframe(comp_df, use_container_width=True)

# --- Financial Summary (Corrected Totals) ---
st.markdown("### 📋 Total Pre-Retirement Income Summary")

# Build the income types and values based on scenario
income_labels = ["VSIP Lump Sum"]
income_values = [vsip_amount]

if disability_retirement:
    income_labels.append("Annual FERS Pension (Disability Retirement)")
    income_values.append(fers_disability)
else:
    income_labels.append("Annual FERS Pension (Regular FERS Retirement)")
    income_values.append(fers_regular)
    if srs_annual > 0:
        income_labels.append("Special Retirement Supplement (SRS)")
        income_values.append(srs_annual)

# Always add VA Disability if present
if va_monthly > 0:
    income_labels.append("Annual VA Disability")
    income_values.append(va_monthly * 12)

# Build the DataFrame
summary_data = {
    "Income Type": income_labels,
    "Amount ($)": income_values
}
summary_df = pd.DataFrame(summary_data)

total_preretirement_income = sum(income_values)

st.dataframe(summary_df.style.format({"Amount ($)": "${:,.2f}"}), use_container_width=True)
st.success(f"**Combined Pre-Retirement Income:** ${total_preretirement_income:,.2f}")


# --- Net Cash After Expenses ---
total_expenses = (fehb_premium + fegli_premium + monthly_expenses) * 12
net_cash = total_preretirement_income - total_expenses

st.markdown("### 💰 Net Cash After Expenses")
st.info(f"**Annual Expenses (FEHB + FEGLI + Living):** ${total_expenses:,.2f}")
st.success(f"**Net Cash Flow:** ${net_cash:,.2f}")

# --- GPT Tool Link ---
st.markdown("### 💬 Need Personalized TSP or Retirement Strategy Help?")
st.markdown("[🧠 Ask Simforia’s TSP Advisor GPT — Smart Projections, Risk Modeling, and Tax-Aware Retirement Analysis](https://chat.openai.com/g/g-67eea2244d2c819189bee5201afec0bc-tsp-advisor-by-simforia-intellegence-group)")

# --- Footer ---
st.markdown("---")
st.markdown("**Contact Simforia Intelligence Group**")
st.markdown("""
<form action="https://formspree.io/f/mzzejjkk" method="POST">
  <label>Your message:<br><textarea name="message"></textarea></label><br>
  <label>Your email (optional):<br><input type="email" name="email"></label><br>
  <button type="submit">Send</button>
</form>
""", unsafe_allow_html=True)

st.markdown("""
---
<small><strong>Disclaimer:</strong> This simulation tool is provided strictly for educational and informational purposes. It does not constitute official retirement guidance, legal counsel, financial advice, or tax planning. This tool is not affiliated with, endorsed by, or authorized by the Office of Personnel Management (OPM), the Department of Defense (DoD), or any federal agency. All estimates are based on simplified assumptions and publicly available retirement formulas and should not be used for final decision-making. Individual circumstances, benefit eligibility, agency-specific policies, and future changes to law or policy may significantly alter results. Before acting on any output from this tool, you are strongly advised to consult your Human Resources office, a certified financial planner, tax professional, and/or retirement counselor. Use of this app constitutes acknowledgment that Simforia Intelligence Group assumes no liability for outcomes or decisions made from its use.</small>
""", unsafe_allow_html=True)

