# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt

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
    5. Choose VERA, VSIP, and DRP options if eligible.
    """)

# --- Inputs ---
current_age = st.number_input("Current Age", min_value=18, max_value=80)
years_service = st.number_input("Years of Federal Service", min_value=0, max_value=50)
high3_salary = st.number_input("High-3 Average Salary ($)", min_value=0)
tsp_balance = st.number_input("Current TSP Balance ($)", min_value=0)
tsp_contribution_pct = st.slider("TSP Contribution (% of Salary)", 0, 100, 5)
tsp_contribution_annual = high3_salary * (tsp_contribution_pct / 100)

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

# --- Pre-Retirement Income Summary ---
st.markdown("### 📋 Total Pre-Retirement Income Summary")
total_preretirement_income = vsip_amount + total_admin_leave_income
st.write(f"**Total DRP Leave Pay:** ${total_admin_leave_income:,.2f}")
st.write(f"**VSIP Lump Sum:** ${vsip_amount:,.2f}")
st.success(f"**Combined Pre-Retirement Income:** ${total_preretirement_income:,.2f}")

# --- Net Worth Over Time (Simulation) ---
st.markdown("### 📈 Projected Net Worth Over Time")
cash_savings = total_preretirement_income  # starting with DRP + VSIP
tsp_growth_rate = 0.05
fers_pension_annual = 0.01 * high3_salary * years_service
annual_expenses = 40000

net_worth = []
years = list(range(current_age, 86))

for year in years:
    cash_savings += cash_savings * 0.02  # safe yield (2%)
    tsp_balance += tsp_balance * tsp_growth_rate
    cash_savings += fers_pension_annual
    cash_savings -= annual_expenses
    net_worth.append(cash_savings + tsp_balance)

fig, ax = plt.subplots()
ax.plot(years, net_worth, marker='o')
ax.set_title("Projected Net Worth Timeline")
ax.set_xlabel("Age")
ax.set_ylabel("Total Net Worth ($)")
ax.grid(True)
st.pyplot(fig)
