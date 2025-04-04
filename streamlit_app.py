# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime

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
    """)

# --- Inputs ---
current_age = st.number_input("Current Age", min_value=18, max_value=80)
years_service = st.number_input("Years of Federal Service", min_value=0, max_value=50)
high3_salary = st.number_input("High-3 Average Salary ($)", min_value=0)
tsp_balance = st.number_input("Current TSP Balance ($)", min_value=0)
tsp_contribution_pct = st.slider("TSP Contribution (% of Salary)", 0, 100, 5)
tsp_contribution_annual = high3_salary * (tsp_contribution_pct / 100)

# --- FEHB & FEGLI Selection ---
st.markdown("### Benefit Coverage Costs")
fehb_plan = st.selectbox("FEHB Plan Type", ["None", "Self Only", "Self + One", "Family"])
fehb_costs = {"None": 0, "Self Only": 300, "Self + One": 550, "Family": 750}
fehb_premium = fehb_costs[fehb_plan]

fegli_option = st.selectbox("FEGLI Option", ["None", "Basic", "Basic + Option A", "Basic + Option B"])
fegli_costs = {"None": 0, "Basic": 50, "Basic + Option A": 70, "Basic + Option B": 90}
fegli_premium = fegli_costs[fegli_option]

monthly_expenses = st.number_input("Other Monthly Living Expenses ($)", min_value=0, value=3000)

# --- Pension & SRS ---
fers_multiplier = 0.01
survivor_reduction = 0.10
fers_annuity = high3_salary * fers_multiplier * years_service * (1 - survivor_reduction)
fers_monthly = round(fers_annuity / 12, 2)
srs = (years_service / 40) * (1800 * 12) if current_age < 62 and years_service >= 20 else 0
srs_text = f"${srs:,.2f} annually until age 62" if srs > 0 else "Not eligible or over 62"

# --- Retirement Milestones ---
st.markdown("### Retirement Milestones")
dob_year = datetime.now().year - current_age
milestones = {
    "MRA (Minimum Retirement Age)": 57,
    "59½ (Penalty-Free Withdrawals)": 59.5,
    "Age 62 (Full FERS Eligibility)": 62,
    "Age 65 (Medicare Eligibility)": 65,
    "Age 73 (RMDs Begin)": 73
}
for label, age in milestones.items():
    st.write(f"**{label}**: Age {age} → Year **{int(dob_year + age)}**")

# --- TSP Custom Allocation Projection ---
st.markdown("### Project TSP Growth with Custom Fund Allocation")
alloc_g = st.slider("G Fund (%)", 0, 100, 40)
alloc_f = st.slider("F Fund (%)", 0, 100, 10)
alloc_c = st.slider("C Fund (%)", 0, 100, 25)
alloc_s = st.slider("S Fund (%)", 0, 100, 15)
alloc_i = st.slider("I Fund (%)", 0, 100, 10)
total_alloc = alloc_g + alloc_f + alloc_c + alloc_s + alloc_i

average_returns = {"G": 0.02, "F": 0.04, "C": 0.10, "S": 0.11, "I": 0.07}
future_tsp = tsp_balance
years_until_62 = max(0, 62 - current_age)

if total_alloc == 100:
    allocation = {
        "G": alloc_g / 100,
        "F": alloc_f / 100,
        "C": alloc_c / 100,
        "S": alloc_s / 100,
        "I": alloc_i / 100
    }
    for _ in range(int(years_until_62)):
        total_return = sum(allocation[f] * average_returns[f] for f in allocation)
        future_tsp = (future_tsp + tsp_contribution_annual) * (1 + total_return)
    st.success(f"Projected TSP Balance at Age 62: ${future_tsp:,.2f}")
else:
    st.error("⚠️ Fund allocations must total 100%.")

# --- Net Income Summary ---
st.markdown("### Monthly Income Estimate")
tsp_draw = 1800
total_income = fers_monthly + tsp_draw
total_deductions = fehb_premium + fegli_premium + monthly_expenses
net_monthly = round(total_income - total_deductions, 2)

st.write(f"**FERS Monthly Pension:** ${fers_monthly:,.2f}")
st.write(f"**Estimated TSP Draw:** ${tsp_draw:,.2f}")
st.write(f"**FEHB Premium:** ${fehb_premium:,.2f}")
st.write(f"**FEGLI Premium:** ${fegli_premium:,.2f}")
st.write(f"**Living Expenses:** ${monthly_expenses:,.2f}")
st.success(f"**Net Monthly Income:** ${net_monthly:,.2f}")

# --- SRS Info ---
st.markdown("### Special Retirement Supplement (SRS)")
st.write(f"**SRS Eligibility:** {srs_text}")
if srs > 0:
    st.write(f"**SRS Monthly (Until 62):** ${round(srs / 12, 2):,.2f}")

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
<small><strong>Disclaimer:</strong> This tool provides general estimates for educational use only. Not affiliated with OPM, DoD, or any federal agency. Consult HR or a certified advisor before making retirement decisions.</small>
""", unsafe_allow_html=True)
