# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import urllib.parse
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- Setup & Session State ---
st.session_state.setdefault("visits", 0)
st.session_state.visits += 1

st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-size: 18px !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div style="text-align: center;">
    <h2 style="margin-bottom: 0;">Simforia Intelligence Group</h2>
    <p style='font-size: 18px; margin-top: 0;'><em>Retirement Optimization Toolkit – DRP / VERA / TSP Strategy Suite</em></p>
    <small><strong>Important Notice: For Informational Purposes Only</strong><br></small>
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

# --- FAQ / Help Section ---
with st.expander("❓ FAQ / Help"):
    st.markdown("""
    **SEPP (Substantially Equal Periodic Payments):**  
    A method to withdraw from your retirement savings without incurring the 10% early withdrawal penalty if you retire before age 59½. Payments are fixed and continue for at least 5 years or until you reach 59½ (whichever is longer).
    
    **Age 55 Rule:**  
    For federal employees retiring directly (like via VERA) at age 55 or older in the same calendar year, TSP withdrawals are penalty-free.
    
    **Pension Calculations:**  
    - **Regular FERS Pension:** Calculated as High-3 Salary * 1% * Years of Service * 0.9  
    - **Disability FERS Pension:** Calculated as High-3 Salary * (0.6 if under 62, otherwise 0.4)
    
    Adjust the inputs above to see how changes in your service years or salary impact your final pension.
    """)

# --- Inputs ---
current_age = st.number_input("Current Age", min_value=18, max_value=80)
years_service = st.number_input("Years of Federal Service", min_value=0, max_value=50)
high3_salary = st.number_input("High-3 Average Salary ($)", min_value=0)
tsp_balance = st.number_input("Current TSP Balance ($)", min_value=0)
tsp_contribution_pct = st.slider("TSP Contribution (% of Salary)", 0, 100, 5)
tsp_contribution_annual = high3_salary * (tsp_contribution_pct / 100)

# --- TSP Withdrawal Calculation (For VERA Retirement) ---
st.markdown("### TSP Withdrawal Calculation (For VERA Retirement)")
tsp_option = st.radio("Select TSP Withdrawal Option:", 
                      ("Withdraw now (penalty applies if under 55)",
                       "Delay withdrawal until 59½ (No withdrawal now)",
                       "Set up SEPP plan"))
if current_age < 55:
    if tsp_option == "Withdraw now (penalty applies if under 55)":
         tsp_withdrawal_balance = tsp_balance * 0.9  # 10% penalty applies
         penalty_note = "A 10% penalty applies on withdrawal."
    elif tsp_option == "Set up SEPP plan":
         tsp_withdrawal_balance = tsp_balance
         penalty_note = "No penalty applied via SEPP plan."
    else:  # Delay withdrawal until 59½
         tsp_withdrawal_balance = 0
         penalty_note = "No withdrawal now. Funds remain untouched until 59½."
else:
    # For age 55 or older, withdrawal is penalty-free.
    tsp_withdrawal_balance = tsp_balance
    penalty_note = "Withdrawal is penalty-free."

st.info(penalty_note)
# For this example, we assume a 4% annual withdrawal rate on the accessible TSP balance.
tsp_annual_income = tsp_withdrawal_balance * 0.04
st.markdown(f"**Estimated Annual TSP Income:** ${tsp_annual_income:,.2f}")

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

# --- Pension Calculation Breakdown ---
with st.expander("🔎 Pension Calculation Breakdown"):
    st.markdown("**Regular FERS Pension Calculation:**")
    st.markdown(f"High-3 Salary * 1% * Years of Service * 0.9 = {high3_salary} * 0.01 * {years_service} * 0.9 = ${fers_regular:,.2f}")
    st.markdown("**Disability FERS Pension Calculation:**")
    st.markdown(f"High-3 Salary * (0.6 if under 62 else 0.4) = {high3_salary} * (0.6 if {current_age} < 62 else 0.4) = ${fers_disability:,.2f}")

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

# --- Financial Summary ---
st.markdown("### 📋 Total Pre-Retirement Income Summary")
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
if va_monthly > 0:
    income_labels.append("Annual VA Disability")
    income_values.append(va_monthly * 12)
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
if net_cash >= 0:
    st.success(f"**Net Cash Flow:** ${net_cash:,.2f}")
else:
    st.error(f"**Net Cash Flow:** ${net_cash:,.2f}")

# --- Sensitivity Analysis: Net Cash Flow vs. Years of Service ---
with st.expander("🔍 Sensitivity Analysis: Net Cash Flow vs. Years of Service"):
    years_range = list(range(0, 51))
    net_cash_sensitivity = []
    for y in years_range:
        pension_value = high3_salary * 0.01 * y * 0.9
        total_income = vsip_amount + pension_value
        total_exp = (fehb_premium + fegli_premium + monthly_expenses) * 12
        net_cash_sensitivity.append(total_income - total_exp)
    fig, ax = plt.subplots()
    ax.plot(years_range, net_cash_sensitivity, marker='o')
    ax.set_title("Net Cash Flow vs. Years of Service")
    ax.set_xlabel("Years of Federal Service")
    ax.set_ylabel("Net Cash Flow ($)")
    st.pyplot(fig)

# --- Cash Flow Projection Over Time ---
with st.expander("🔍 Cash Flow Projection Over Time"):
    projection_years = list(range(0, 21))
    growth_rate = 0.02
    projected_cash_flows = [net_cash * ((1 + growth_rate) ** i) for i in projection_years]
    fig2, ax2 = plt.subplots()
    ax2.plot(projection_years, projected_cash_flows, marker='o', color='blue')
    ax2.set_title("Projected Net Cash Flow Over 20 Years")
    ax2.set_xlabel("Years After Retirement")
    ax2.set_ylabel("Projected Net Cash Flow ($)")
    st.pyplot(fig2)

# --- Export Detailed Calculation Data as CSV ---
with st.expander("📤 Export Detailed Calculation Data"):
    data = {
         "Metric": [
             "Current Age",
             "Years of Service",
             "High-3 Salary",
             "TSP Balance",
             "TSP Contribution Rate",
             "Regular FERS Pension",
             "Disability FERS Pension",
             "Selected FERS Income",
             "Special Retirement Supplement (SRS)",
             "Annual VA Disability",
             "VSIP Lump Sum",
             "Total Pre-Retirement Income",
             "Annual Expenses",
             "Net Cash Flow",
             "Accessible TSP Balance",
             "Estimated Annual TSP Income"
         ],
         "Value": [
             current_age,
             years_service,
             high3_salary,
             tsp_balance,
             tsp_contribution_pct,
             fers_regular,
             fers_disability,
             selected_fers_income,
             srs_annual,
             va_monthly * 12,
             vsip_amount,
             total_preretirement_income,
             total_expenses,
             net_cash,
             tsp_withdrawal_balance,
             tsp_annual_income
         ]
    }
    export_df = pd.DataFrame(data)
    csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Detailed Data as CSV",
                       data=csv,
                       file_name="detailed_calculation_data.csv",
                       mime="text/csv")

# --- PDF Retirement Report Generator ---
st.markdown("### 🖨️ Download Your Personalized Retirement Report")
buffer = io.BytesIO()
p = canvas.Canvas(buffer, pagesize=letter)
width, height = letter

# Header
p.setFont("Helvetica-Bold", 16)
p.drawString(50, 750, "Simforia Retirement Summary Report")
p.line(50, 747, 550, 747)

# User Data Section
p.setFont("Helvetica", 12)
y = 720
user_info = [
    f"Current Age: {current_age}",
    f"Years of Federal Service: {years_service}",
    f"High-3 Salary: ${high3_salary:,.2f}",
    f"TSP Balance: ${tsp_balance:,.2f}",
    f"TSP Contribution Rate: {tsp_contribution_pct}%",
    f"FEHB Plan: {fehb_plan} (${fehb_premium}/mo)",
    f"FEGLI Option: {fegli_option} (${fegli_premium}/mo)",
    f"Living Expenses: ${monthly_expenses:,.2f}/mo",
    f"VA Disability: ${va_monthly}/mo",
    f"Pension Type: {pension_label}"
]
for item in user_info:
    p.drawString(50, y, item)
    y -= 20

# TSP Withdrawal Details Section
y -= 10
p.setFont("Helvetica-Bold", 12)
p.drawString(50, y, "TSP Withdrawal Details:")
p.setFont("Helvetica", 12)
y -= 20
tsp_details = [
    f"TSP Withdrawal Option: {tsp_option}",
    f"Penalty Note: {penalty_note}",
    f"Accessible TSP Balance: ${tsp_withdrawal_balance:,.2f}",
    f"Estimated Annual TSP Income: ${tsp_annual_income:,.2f}"
]
for detail in tsp_details:
    p.drawString(50, y, detail)
    y -= 20

# Income Summary Section
y -= 10
p.setFont("Helvetica-Bold", 12)
p.drawString(50, y, "Income Summary:")
p.setFont("Helvetica", 12)
y -= 20
if vsip_amount > 0:
    p.drawString(50, y, f"- VSIP Lump Sum: ${vsip_amount:,.2f}")
    y -= 20
p.drawString(50, y, f"- FERS Pension: ${selected_fers_income:,.2f}")
y -= 20
if not disability_retirement and srs_annual > 0:
    p.drawString(50, y, f"- SRS (Special Retirement Supplement): ${srs_annual:,.2f}")
    y -= 20
if va_monthly > 0:
    p.drawString(50, y, f"- Annual VA Disability: ${va_monthly * 12:,.2f}")
    y -= 30

# Totals Section
p.setFont("Helvetica-Bold", 12)
p.drawString(50, y, f"📊 Total Pre-Retirement Income: ${total_preretirement_income:,.2f}")
y -= 20
p.drawString(50, y, f"🧾 Annual Expenses: ${total_expenses:,.2f}")
y -= 20
p.drawString(50, y, f"💰 Net Cash Flow: ${net_cash:,.2f}")

p.save()
buffer.seek(0)
st.download_button(
    label="📄 Download PDF Retirement Report",
    data=buffer,
    file_name="Retirement_Report.pdf",
    mime="application/pdf"
)

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


