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
st.session_state.setdefault("visits", 1336)
st.session_state.visits += 1

st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            font-size: 18px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Visit Counter ---
st.write(f"You have visited this page {st.session_state.visits} times.")

# --- Header ---
# (Continue with your header code here...)

st.markdown(
    """
<div style="text-align: center;">
    <h2 style="margin-bottom: 0;">Simforia Intelligence Group</h2>
    <p style='font-size: 18px; margin-top: 0;'><em>Retirement Optimization Toolkit – DRP / VERA / TSP Strategy Suite</em></p>
    <small><strong>Important Notice: For Informational Purposes Only</strong><br></small>
</div>
""",
    unsafe_allow_html=True
)

# --- Instructions ---
with st.expander("ℹ️ How to Use This Tool"):
    st.markdown(
        """
    1. Enter your current age and total federal service.
    2. Input your TSP balance, high-3 salary, and contribution rate.
    3. Select your FEHB/CHAMPVA and FEGLI retirement coverage.
    4. View projected growth, income, and milestone ages.
    5. Compare monthly income streams.
    6. Visualize projected net worth including VA, TSP, FERS, SRS, FEHB, and DRP.
    """
    )

# --- FAQ / Help Section ---
with st.expander("❓ FAQ / Help"):
    st.markdown(
        """
**SEPP (Substantially Equal Periodic Payments):**  
A method to withdraw from your retirement savings without incurring the 10% early withdrawal penalty if you retire before age 59½. Payments are fixed and continue for at least 5 years or until you reach 59½ (whichever is longer).

**Age 55 Rule:**  
For federal employees retiring directly (like via VERA) at age 55 or older in the same calendar year, TSP withdrawals are penalty-free.

**Pension Calculations:**  
- **Regular FERS Pension:** Calculated as High-3 Salary * 1% * Years of Service * 0.9  
- **Disability FERS Pension:** Calculated as High-3 Salary * (0.6 if under 62, otherwise 0.4)

Adjust the inputs above to see how changes in your service years or salary impact your final pension.

See our GPT link at the bottom of the page for any complex questions.
        """
    )

# --- Inputs ---
# --- Inputs with Enhanced Tooltips ---
current_age = st.number_input(
    "Current Age", 
    min_value=18, 
    max_value=80, 
    help="Enter your current age in years (must be between 18 and 80)."
)
years_service = st.number_input(
    "Years of Federal Service", 
    min_value=0, 
    max_value=50, 
    help="Enter the total number of years you have worked in federal service."
)
high3_salary = st.number_input(
    "High-3 Average Salary ($)", 
    min_value=0, 
    help="Enter your average salary over your three highest consecutive years of service."
)
tsp_balance = st.number_input(
    "Current TSP Balance ($)", 
    min_value=0, 
    help="Enter your current Thrift Savings Plan balance."
)
tsp_contribution_pct = st.slider(
    "TSP Contribution (% of Salary)", 
    0, 
    100, 
    5, 
    help="Select the percentage of your salary that you contribute to your TSP."
)
tsp_contribution_annual = high3_salary * (tsp_contribution_pct / 100)

# --- Retirement Eligibility ---
retirement_eligibility = st.radio(
    "Are you eligible for federal retirement?",
    ("Eligible", "Not Eligible"),
    help="Select 'Eligible' if you meet the service requirements for federal retirement benefits. Select 'Not Eligible' if you left federal service before qualifying for retirement benefits. In the 'Not Eligible' scenario, your federal pension values will be set to $0."
)

# --- TSP Withdrawal Calculation (For VERA Retirement) ---
st.markdown("### TSP Withdrawal Calculation (For VERA Retirement)")

tsp_option = st.radio(
    "Select TSP Withdrawal Option (Note: Early withdrawals may incur penalties and tax withholdings):",
    (
        "Withdraw now (penalty applies if under 59½)",
        "Delay withdrawal until 59½ (No withdrawal now)",
        "Set up SEPP plan",
    ),
    help="Choose 'Withdraw now' for immediate funds (subject to a 10% early withdrawal penalty and tax withholding if under 59½), 'Set up SEPP plan' to avoid the penalty (but taxes still apply), or 'Delay withdrawal' to defer until 59½."
)

# --- TSP Penalty and Tax Logic (Enhanced by Age, Service, VERA Eligibility) ---
# --- VERA Eligibility Checkbox ---
# --- Public Safety Employee Exception ---
public_safety_employee = st.checkbox(
    "I am a public safety employee (LEO, Firefighter, Air Traffic Controller)",
    value=False,
    help="Check if you are covered under special retirement provisions for public safety employees. TSP early withdrawal penalties may not apply if you separate at age 50 or later."
)

vera_elected = st.checkbox(
    "I am retiring under a VERA (Voluntary Early Retirement Authority)",
    value=False,
    help="Check this if you are separating under the VERA program (typically 25+ years of service and at least age 50)."
)

def calculate_tsp_penalty_status(age, years_service, vera_elected, public_safety_employee):
    if public_safety_employee and age >= 50:
        return False, "No penalty – Public safety employee separated at or after age 50."

    if age >= 62 and years_service >= 5:
        return False, "No penalty – Age 62 or older at separation."
    elif age >= 60 and years_service >= 20:
        return False, "No penalty – Age 60+ with 20+ years of service."
    elif age >= 55:
        if vera_elected or years_service >= 30:
            return False, "No penalty – Age 55 Rule applies (VERA or 30+ years)."
        else:
            return False, "No penalty – Age 55 Rule applies."
    elif age >= 50 and vera_elected and years_service >= 25:
        return True, "10% penalty – VERA retirement under age 55."
    else:
        return True, "10% penalty – Not retirement eligible under TSP rules."


# Apply rule
tsp_penalty_applies, penalty_note = calculate_tsp_penalty_status(
    current_age, years_service, vera_elected, public_safety_employee
)



# --- TSP Withdrawal Rule Reference (Collapsible) ---
with st.expander("📘 TSP Early Withdrawal Rules Explained"):
    st.markdown("""
### 🧮 **TSP Early Withdrawal Rule Summary Table**

| **Age at Separation** | **Years of Service** | **Separation Type** | **Retirement Eligible?** | **10% TSP Penalty?** | **Notes** |
|------------------------|----------------------|-----------------------|----------------------------|------------------------|-----------|
| **62+**                | 5+                   | VERA or Non-VERA      | ✅ Full retirement         | ❌ No                  | Age 62 = no penalty regardless of type |
| **60–61**              | 20+                  | VERA or Non-VERA      | ✅ Full retirement         | ❌ No                  | No penalty if age ≥ 55 at separation |
| **55–59**              | 30+ or MRA+10        | VERA or Non-VERA      | ✅ Full or early retirement| ❌ No                  | Age 55 Rule applies |
| **55–59**              | <30 (e.g., 25–29)    | VERA only             | ✅ Early (via VERA)        | ❌ No                  | Age 55 Rule still applies |
| **50–54**              | 25+                  | ✅ VERA                | ✅ Early retirement        | ✅ Yes                 | Not age 55 → penalty unless exception used |
| **<50**                | Any                  | VERA or Non-VERA      | ❌ Not eligible            | ✅ Yes                 | Ineligible for retirement under FERS |

---

### 🔁 **Key Logic Points**
- **Age 55 at separation** is the penalty cutoff under standard FERS TSP rules.
- **VERA eligibility does NOT automatically waive the TSP penalty** if you're under 55.
- **Public safety employees (LEO, FF, ATC)** may be exempt starting at **age 50**, not reflected here.
- Use this logic to decide whether to delay TSP withdrawals, set up SEPP, or take penalty-hit withdrawals.

    """)


# Slider for estimated federal tax rate on TSP distributions (as a percentage)
tax_rate = st.slider(
    "Estimated Federal Income Tax Rate (%) for TSP Distribution",
    min_value=0,
    max_value=50,
    value=22,
    help="Estimate your marginal tax rate for TSP distributions. This percentage will be applied to early withdrawals."
) / 100.0  # convert to decimal

withdrawal_rate = st.slider(
    "Estimated Annual Withdrawal Rate (%)", 
    min_value=1, 
    max_value=10, 
    value=4,
    help="Select the annual percentage of the accessible TSP balance you plan to withdraw."
)

if current_age < 59.5:
    if tsp_option == "Withdraw now (penalty applies if under 59½)":
        if tsp_penalty_applies:
            base_balance = tsp_balance * 0.90  # Apply 10% penalty
            net_balance = base_balance * (1 - tax_rate)
            penalty_note += " This scenario includes the 10% early withdrawal penalty."
            st.warning("⚠️ You will incur a 10% early withdrawal penalty based on your current age and retirement type.")
        else:
            net_balance = tsp_balance * (1 - tax_rate)
            penalty_note = "No penalty applies, only taxes withheld."
        tsp_withdrawal_balance = net_balance
    elif tsp_option == "Set up SEPP plan":
        net_balance = tsp_balance * (1 - tax_rate)
        tsp_withdrawal_balance = net_balance
        penalty_note = f"No penalty via SEPP plan; an estimated {tax_rate*100:.0f}% tax is withheld."
    else:
        tsp_withdrawal_balance = 0
        penalty_note = "No withdrawal now. Funds remain untouched until 59½."

else:
    net_balance = tsp_balance * (1 - tax_rate)
    tsp_withdrawal_balance = tsp_balance
    penalty_note = f"Withdrawal is penalty-free; an estimated {tax_rate*100:.0f}% tax is applied on distributions."


st.info(penalty_note)
tsp_annual_income = tsp_withdrawal_balance * (withdrawal_rate / 100)
st.markdown(f"**Estimated Annual TSP Income:** ${tsp_annual_income:,.2f}")
tsp_annual_income = tsp_withdrawal_balance * (withdrawal_rate / 100)

# --- FEHB / CHAMPVA & FEGLI Selection ---
st.markdown("### FEHB / CHAMPVA & FEGLI Selection")
health_coverage_choice = st.radio(
    "Select your primary health coverage:",
    ("None", "FEHB", "CHAMPVA"),
    help="Choose 'None' if you do not have primary coverage, 'FEHB' if you are enrolled in the Federal Employees Health Benefits program, or 'CHAMPVA' if you're covered under the CHAMPVA program."
)

if health_coverage_choice == "None":
    fehb_premium = 0
    st.markdown("No primary coverage selected. Make sure this matches your real situation.")
elif health_coverage_choice == "FEHB":
    # If user selects FEHB, let them pick a plan
    fehb_plan = st.selectbox(
        "FEHB Plan Type", 
        ["Self Only", "Self + One", "Family"],
        help="Select the plan type for FEHB. 'Self Only' covers you alone, 'Self + One' covers you and one dependent, and 'Family' covers your entire family."
    )
    fehb_costs = {"Self Only": 300, "Self + One": 550, "Family": 750}
    fehb_premium = fehb_costs[fehb_plan]
    st.markdown(f"**Selected FEHB Plan:** {fehb_plan}, Monthly Premium = ${fehb_premium}")
elif health_coverage_choice == "CHAMPVA":
    fehb_premium = 0  # For simulation: No FEHB cost if using CHAMPVA
    st.markdown(
        """
    **CHAMPVA** (Civilian Health and Medical Program of the Department of Veterans Affairs)
    is a comprehensive health care benefits program in which the VA shares the cost of covered
    health care services and supplies with eligible beneficiaries.
    [More Info](https://www.va.gov/COMMUNITYCARE/programs/dependents/champva/)
    """,
        unsafe_allow_html=True
    )
    st.markdown("No additional monthly premium is assumed here for demonstration.")

fegli_option = st.selectbox(
    "FEGLI Option", 
    ["None", "Basic", "Basic + Option A", "Basic + Option B"],
    help="Select your FEGLI option. 'Basic' is the standard coverage, while 'Basic + Option A' and 'Basic + Option B' offer additional benefits at higher premiums."
)
fegli_costs = {"None": 0, "Basic": 50, "Basic + Option A": 70, "Basic + Option B": 90}
fegli_premium = fegli_costs[fegli_option]

monthly_expenses = st.number_input(
    "Other Monthly Living Expenses ($)", 
    min_value=0, 
    value=3000,
    help="Enter your average monthly living expenses (e.g., housing, food, utilities, etc.)."
)

# --- VA Disability & Disability Retirement Option ---
st.markdown("### VA Disability Compensation")
va_monthly = st.number_input(
    "Monthly VA Disability Payment ($)", 
    min_value=0, 
    value=0,
    help="Enter the monthly VA disability payment amount. Use 0 if not applicable."
)

st.markdown("### Disability Retirement")
disability_retirement = st.checkbox(
    "Apply FERS Disability Retirement Calculation Instead?",
    help="Check this box if you plan to retire on disability, which uses a different pension calculation."
)

# --- SRS Calculation ---
srs = (years_service / 40) * (1800 * 12) if current_age < 62 and years_service >= 20 else 0
srs_annual = srs if current_age < 62 else 0


# --- Separation Incentives: VERA / VSIP / DRP Options ---
st.markdown("### Separation Incentives")
vera_elected = st.checkbox(
    "Elect Voluntary Early Retirement Authority (VERA)?",
    help="Check this if you're eligible for VERA retirement (e.g., 20 years at age 50 or 25 years at any age)."
)
vsip_amount = st.number_input(
    "VSIP Offer Amount ($, if applicable)",
    min_value=0,
    help="Enter the lump sum offered under the VSIP program, if applicable."
)
drp_elected = st.checkbox(
    "Participating in DoD Deferred Resignation Program (DRP)?",
    help="Check this if you're participating in DRP, which may include paid administrative leave."
)

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
    months_of_leave = st.slider(
        "Months of Paid Leave Before Separation",
        min_value=1,
        max_value=5,
        value=4,
        help="Select the number of months you will receive paid leave if participating in DRP."
    )
    monthly_salary = high3_salary / 12
    total_admin_leave_income = months_of_leave * monthly_salary
    st.write(f"**Estimated Admin Leave Income (Before Final Separation):** ${total_admin_leave_income:,.2f}")

# --- Pension Calculations & Scenario Selection ---
if retirement_eligibility == "Not Eligible":
    fers_regular = 0
    fers_disability = 0
    monthly_regular = 0
    monthly_disability = 0
else:
    fers_regular = high3_salary * 0.01 * years_service * 0.9
    fers_disability = high3_salary * (0.6 if current_age < 62 else 0.4)
    monthly_regular = round(fers_regular / 12, 2)
    monthly_disability = round(fers_disability / 12, 2)

if disability_retirement:
    selected_fers_income = fers_disability
    selected_monthly_income = monthly_disability
    pension_label = "Disability Retirement"
else:
    selected_fers_income = fers_regular
    selected_monthly_income = monthly_regular
    pension_label = "Regular FERS Retirement"

with st.expander("🔎 Pension Calculation Breakdown"):
    st.markdown("**Regular FERS Pension Calculation:**")
    st.markdown(
        f"High-3 Salary * 1% * Years of Service * 0.9 = {high3_salary} * 0.01 * {years_service} * 0.9 = ${fers_regular:,.2f}"
    )
    st.markdown("**Disability FERS Pension Calculation:**")
    st.markdown(
        f"High-3 Salary * (0.6 if {current_age} < 62 else 0.4) = {high3_salary} * (0.6) = ${fers_disability:,.2f}"
    )

# --- What-if Comparison: Disability vs. Regular Retirement (Enhanced) ---
st.markdown("### 🧮 What-if Comparison: Disability vs. Regular Retirement")


show_diff = st.checkbox("Show Percentage Difference between Scenarios", value=True, 
                          help="Toggle to display the percentage difference in annual pension between Disability and Regular FERS scenarios.")

comparison_data = {
    "Scenario": ["Regular FERS Retirement", "Disability Retirement"],
    "Annual Pension ($)": [fers_regular, fers_disability],
    "Monthly Pension ($)": [monthly_regular, monthly_disability],
    "SRS Eligible": ["Yes" if srs > 0 else "No"] * 2,
    "VA Monthly Added ($)": [va_monthly] * 2,
    "FEHB/FEGLI Annual Cost ($)": [(fegli_premium + fehb_premium) * 12] * 2,
}

df_compare = pd.DataFrame(comparison_data)

if show_diff:
    # Calculate percentage difference between Disability and Regular Annual Pension
    # For Regular scenario, set difference as 0, for Disability, compute the percentage difference
    if fers_regular != 0:
        diff_pct = ((fers_disability - fers_regular) / fers_regular) * 100
    else:
        diff_pct = 0
    # Append a new column that is 0 for Regular and diff_pct for Disability scenario
    df_compare["Difference (%)"] = [0, diff_pct]

# Format the DataFrame for display
df_compare = df_compare.style.format({
    "Annual Pension ($)": "${:,.2f}",
    "Monthly Pension ($)": "${:,.2f}",
    "VA Monthly Added ($)": "${:,.2f}",
    "FEHB/FEGLI Annual Cost ($)": "${:,.2f}",
    "Difference (%)": "{:+.2f}%"
})

st.dataframe(df_compare, use_container_width=True)

# --- Pro/Con Analysis for Retirement Scenarios ---
st.markdown("### Pro/Con Analysis for Retirement Scenarios")
st.markdown("Define your priorities for retirement decisions below:")
priority_income = st.slider(
    "Importance of Immediate Income (1-10)",
    min_value=1, max_value=10, value=5,
    help="How important is having immediate cash flow after retirement?"
)
priority_security = st.slider(
    "Importance of Long-Term Security (1-10)",
    min_value=1, max_value=10, value=5,
    help="How important is a stable, long-term pension benefit?"
)
priority_flexibility = st.slider(
    "Importance of Flexibility (1-10)",
    min_value=1, max_value=10, value=5,
    help="How important is having flexibility in retirement options?"
)

# Create sample pro/con data for demonstration
pro_con_data = {
    "Scenario": [
        "Regular FERS Retirement", 
        "Disability Retirement", 
        "VERA", 
        "DRP"
    ],
    "Pros": [
        f"Steady pension; meets long-term security (Income Score: {priority_income})",
        f"Higher initial payout and potential SRS boost (Income Score: {priority_income + 1})",
        f"Early retirement with strong benefits (Flexibility Score: {priority_flexibility})",
        f"Additional lump sum and admin leave income (Security Score: {priority_security})"
    ],
    "Cons": [
        f"Lower early payout; slower growth (Risk Score: {10 - priority_income})",
        f"Reduced pension multiplier if under 62 (Risk Score: {10 - priority_security})",
        f"Requires strict service criteria; uncertain outcomes (Flexibility Risk: {10 - priority_flexibility})",
        f"Complex rules and potential short-term income gap (Overall Risk: {10 - (priority_income + priority_security)//2})"
    ]
}
df_pro_con = pd.DataFrame(pro_con_data)
st.dataframe(df_pro_con, use_container_width=True)

# --- Career Continuation vs. Retirement Wage Analysis ---
st.markdown("### Career Continuation vs. Retirement Wage Analysis")
st.markdown("Enter your current career details to compare potential continued wages with estimated retirement wages:")

current_grade = st.number_input(
    "Enter your current grade", 
    min_value=1, max_value=20, value=10,
    help="Your current federal grade level."
)
current_step = st.number_input(
    "Enter your current step", 
    min_value=1, max_value=10, value=5,
    help="Your current step within your grade."
)
local_wage = st.number_input(
    "Enter your current annual local wage ($)", 
    min_value=0, value=60000,
    help="Your current annual salary based on local cost of living."
)
expected_retirement_multiplier = st.slider(
    "Expected Retirement Wage Multiplier", 
    min_value=1.0, max_value=2.0, value=1.5, step=0.1,
    help="An estimated factor by which your retirement wage may differ from your current wage."
)

# Hypothetical formulas (adjust these as needed)
estimated_retirement_wage = local_wage * expected_retirement_multiplier
projected_career_wage = local_wage + (current_grade * current_step * 1000)  # Example formula

wage_comparison = {
    "Category": ["Estimated Retirement Wage", "Projected Continued Career Wage"],
    "Annual Wage ($)": [estimated_retirement_wage, projected_career_wage]
}
df_wage = pd.DataFrame(wage_comparison)
st.dataframe(df_wage.style.format({"Annual Wage ($)": "${:,.2f}"}), use_container_width=True)

st.markdown("""
**Analysis:**
- **Retirement Wage:** This is a simplified estimate based on a multiplier applied to your current wage.
- **Continued Career Wage:** This rough estimate factors in potential grade and step increases.
Compare these figures to see which path might yield a better financial outcome, considering both long-term stability and short-term earning potential.
""")


# --- Additional Expense Inputs (Enhanced) ---
debt_payments = st.number_input(
    "Monthly Debt Payments ($)", 
    min_value=0, 
    value=0,
    help="Enter your total monthly debt payments (e.g., loans, credit card payments)."
)
healthcare_expenses = st.number_input(
    "Monthly Healthcare Expenses ($)", 
    min_value=0, 
    value=0,
    help="Enter your estimated monthly healthcare costs not covered by insurance."
)
additional_taxes = st.number_input(
    "Estimated Annual Additional Taxes ($)", 
    min_value=0, 
    value=0,
    help="Enter any additional annual taxes not included in your regular expense calculations."
)

# --- Currency Selection ---
currency_symbol = st.selectbox(
    "Select Currency Symbol", 
    options=["$", "€", "£", "¥"], 
    index=0,
    help="Choose your currency symbol for displaying amounts."
)

# --- Enhanced Financial Summary & Net Cash Flow ---
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
    "Amount": income_values,
}
summary_df = pd.DataFrame(summary_data)
total_preretirement_income = sum(income_values)

st.dataframe(summary_df.style.format({"Amount": f"{currency_symbol}{{:,.2f}}"}), use_container_width=True)
st.success(f"**Combined Pre-Retirement Income:** {currency_symbol}{total_preretirement_income:,.2f}")

# Update total expenses to include additional categories
base_expenses = (fegli_premium + fehb_premium + monthly_expenses) * 12
debt_expenses = debt_payments * 12
healthcare_total = healthcare_expenses * 12
total_expenses = base_expenses + debt_expenses + healthcare_total + additional_taxes

net_cash = total_preretirement_income - total_expenses

st.markdown("### 💰 Net Cash After Expenses")
st.info(f"**Annual Expenses (Insurance + Living + Debt + Healthcare + Taxes):** {currency_symbol}{total_expenses:,.2f}")
if net_cash >= 0:
    st.success(f"**Net Cash Flow:** {currency_symbol}{net_cash:,.2f}")
else:
    st.error(f"**Net Cash Flow:** {currency_symbol}{net_cash:,.2f}")

# --- Graphical Visualization: Income vs. Expenses ---
st.markdown("### 📊 Income vs. Expenses Comparison")
fig_income, ax_income = plt.subplots()
categories = ['Total Income', 'Total Expenses']
values = [total_preretirement_income, total_expenses]
colors = ['green', 'red']
ax_income.bar(categories, values, color=colors)
ax_income.set_title("Total Income vs. Total Expenses")
ax_income.set_ylabel(f"Amount ({currency_symbol})")
st.pyplot(fig_income)


# --- Contractor Toolkit Section with SRS Earnings Test ---
with st.expander("🛠 Contractor Toolkit (SRS Impact)"):
    st.markdown("### Contractor Income Analysis & SRS Earnings Test")
    
    contractor_role = st.text_input(
        "Contractor Role", 
        "Federal Compliance Consultant",
        help="Enter your role as a contractor (e.g., Federal Compliance Consultant)."
    )
    hourly_rate = st.number_input(
        "Hourly Rate ($)", 
        min_value=0, 
        value=120,
        help="Enter your hourly rate as a contractor."
    )
    hours_per_week = st.number_input(
        "Hours per Week", 
        min_value=0, 
        value=25,
        help="Enter the number of hours you work per week as a contractor."
    )
    weekly_overhead = st.number_input(
        "Weekly Overhead Costs ($)", 
        min_value=0, 
        value=200,
        help="Enter your estimated weekly overhead costs (e.g., equipment, travel, etc.)."
    )
    
    # Calculate annual contractor income components
    annual_gross = hourly_rate * hours_per_week * 52
    annual_overhead = weekly_overhead * 52
    contractor_net_income = annual_gross - annual_overhead
    
    st.markdown(f"**Annual Gross Contractor Income:** ${annual_gross:,.2f}")
    st.markdown(f"**Annual Overhead Costs:** ${annual_overhead:,.2f}")
    if contractor_net_income >= 0:
        st.success(f"**Net Contractor Income:** ${contractor_net_income:,.2f}")
    else:
        st.error(f"**Net Contractor Income:** ${contractor_net_income:,.2f}")
    
    # SRS Earnings Test: Option to apply the test
    apply_srs_earnings_test = st.checkbox(
        "Apply FERS SRS earnings test to contractor income?",
        help="Check this if you want to see how contractor income may reduce your SRS benefit."
    )
    earnings_test_threshold = 21240  # This threshold can be updated as needed.
    
    srs_offset = 0
    adjusted_srs = srs_annual  # Start with no offset.
    if apply_srs_earnings_test and srs_annual > 0:
        if contractor_net_income > earnings_test_threshold:
            over_threshold = contractor_net_income - earnings_test_threshold
            srs_offset = over_threshold / 2  # For every $2 over the threshold, reduce SRS by $1.
        adjusted_srs = max(0, srs_annual - srs_offset)
        
        st.markdown("---")
        st.markdown(f"**Original SRS:** ${srs_annual:,.2f}")
        st.markdown(f"**Earnings Test Threshold:** ${earnings_test_threshold:,.2f}")
        st.markdown(f"**SRS Reduction Due to Contractor Income:** ${srs_offset:,.2f}")
        st.markdown(f"**Adjusted SRS:** ${adjusted_srs:,.2f}")
    
    # Calculate adjusted retirement income and net cash flow with SRS modification
    srs_delta = adjusted_srs - srs_annual
    adjusted_retirement_income = total_preretirement_income + srs_delta
    adjusted_net_cash = adjusted_retirement_income - total_expenses
    
    if apply_srs_earnings_test and srs_offset > 0:
        st.info(f"**Adjusted Retirement Net Cash Flow (with SRS reduction): ${adjusted_net_cash:,.2f}**")
    else:
        st.info(f"**Retirement Net Cash Flow (unchanged): ${adjusted_net_cash:,.2f}**")
    
    # Comparison Chart: Adjusted Retirement vs. Contractor Income
    st.markdown("### Comparison: Adjusted Retirement vs. Contractor Income")
    incomes = {
        "Retirement Net Cash (Adj.)": adjusted_net_cash,
        "Contractor Net Income": contractor_net_income,
    }
    comp_df2 = pd.DataFrame(list(incomes.items()), columns=["Income Source", "Amount"])
    
    fig3, ax3 = plt.subplots()
    colors = ["green" if adjusted_net_cash >= 0 else "red", "blue"]
    ax3.bar(comp_df2["Income Source"], comp_df2["Amount"], color=colors)
    ax3.set_ylabel("Amount ($)")
    ax3.set_title("Income Comparison: Adjusted Retirement vs. Contractor")
    st.pyplot(fig3)
    
    # Save contractor data to session state for later exports (CSV/PDF)
    st.session_state["contractor_role"] = contractor_role
    st.session_state["contractor_net_income"] = contractor_net_income
    st.session_state["contractor_gross_income"] = annual_gross
    st.session_state["contractor_overhead"] = annual_overhead
    st.session_state["srs_offset"] = srs_offset
    st.session_state["adjusted_srs"] = adjusted_srs
    st.session_state["adjusted_retirement_income"] = adjusted_retirement_income
    st.session_state["adjusted_net_cash"] = adjusted_net_cash


# --- Federal Independent Contractor Steps (Enhanced) ---
with st.expander("🧷 Federal Independent Contractor Steps"):
    st.markdown(
        """
**Federal Independent Contractor Steps:**

1. **Determine Your Small Business Status:**  
   - Review the [SBA Table of Size Standards](https://www.sba.gov/document/support--table-size-standards) to determine if your business qualifies as a small business.  
   - Consider your annual revenue and number of employees.

2. **Identify Your NAICS Code:**  
   - Use resources like the [Census NAICS Code Finder](https://www.census.gov/naics/) to match your products or services with the appropriate NAICS code.  
   - A correct NAICS code is essential for federal contracting opportunities.

3. **Set Up Your Business Entity:**  
   - **LLC (Limited Liability Company):**  
     - Provides liability protection similar to a corporation with the tax flexibility of a partnership.  
     - Profits and losses "pass through" to members unless you elect S-corp or C-corp taxation.
   - **S-corporation (S-corp):**  
     - Offers potential tax savings by passing income through to shareholders, with restrictions on the number and type of shareholders.
   - **C-corporation (C-corp):**  
     - Involves corporate taxation and potential double taxation on dividends but allows for more complex capital structures.

4. **Register in the System for Award Management (SAM):**  
   - Mandatory for federal contracting. Visit [SAM.gov](https://sam.gov/) to register your business and obtain a federal tax ID (EIN) if needed.

5. **Explore Contract Opportunities:**  
   - Use [SAM.gov](https://sam.gov/) to search for federal contract solicitations.  
   - Consider subcontracting with established federal contractors to build your track record.

**Additional Guidance:**
Select a question below to get detailed advice or insights through our GPT assistant.
        """
    )

    # Dropdown for GPT Prompts
    contractor_prompts = [
        "What are the key criteria to determine my small business status?",
        "How do I find and select the appropriate NAICS code for my services?",
        "What are the advantages and disadvantages of forming an LLC versus an S-corp?",
        "How do I register in SAM and what documentation is required?",
        "What strategies can I use to explore federal contract opportunities?"
    ]
    selected_prompt = st.selectbox(
        "Select a prompt for further guidance:",
        contractor_prompts,
        help="Choose a question to receive more detailed advice or insights via our GPT assistant."
    )
    st.markdown(f"**Selected Prompt for GPT:** {selected_prompt}")

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
            "Estimated Annual TSP Income",
            "Contractor Role",
            "Contractor Gross Income",
            "Contractor Overhead",
            "Contractor Net Income",
            "SRS Offset (Due to Contractor Income)",
            "Adjusted SRS",
            "Adjusted Retirement Net Cash",
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
            tsp_annual_income,
            st.session_state.get("contractor_role", "N/A"),
            st.session_state.get("contractor_gross_income", 0),
            st.session_state.get("contractor_overhead", 0),
            st.session_state.get("contractor_net_income", 0),
            st.session_state.get("srs_offset", 0),
            st.session_state.get("adjusted_srs", 0),
            st.session_state.get("adjusted_net_cash", net_cash),
        ],
    }
    export_df = pd.DataFrame(data)
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Detailed Data as CSV",
        data=csv,
        file_name="detailed_calculation_data.csv",
        mime="text/csv",
    )


# --- Sensitivity Analysis: Net Cash Flow vs. Years of Federal Service (Enhanced) ---
with st.expander("🔍 Sensitivity Analysis: Net Cash Flow vs. Years of Federal Service (Enhanced)"):
    st.markdown("This analysis uses a simplified pension calculation. Adjust the parameters below to see how changes in assumptions impact your net cash flow over different years of federal service.")
    
    pension_multiplier = st.slider(
        "Pension Multiplier",
        min_value=0.005,
        max_value=0.02,
        value=0.01,
        step=0.001,
        help="Adjust the percentage multiplier used in the pension calculation (default is 1%)."
    )
    
    expense_factor = st.slider(
        "Expense Adjustment Factor",
        min_value=0.8,
        max_value=1.2,
        value=1.0,
        step=0.05,
        help="Adjust overall expense estimates by this factor to simulate variations in living costs."
    )
    
    years_range = list(range(0, 51))
    net_cash_sensitivity = []
    for y in years_range:
        # Recalculate pension using the adjustable multiplier.
        pension_value = high3_salary * pension_multiplier * y * 0.9  # 0.9 factor remains constant.
        total_income = vsip_amount + pension_value
        base_expenses = (fegli_premium + fehb_premium + monthly_expenses) * 12
        total_exp = base_expenses * expense_factor
        net_cash_sensitivity.append(total_income - total_exp)
    
    fig, ax = plt.subplots()
    ax.plot(years_range, net_cash_sensitivity, marker="o")
    ax.set_title("Net Cash Flow vs. Years of Federal Service (Enhanced)")
    ax.set_xlabel("Years of Federal Service")
    ax.set_ylabel("Net Cash Flow ($)")
    st.pyplot(fig)


# --- Cash Flow Projection Over Time (Enhanced) ---
with st.expander("🔍 Cash Flow Projection Over Time"):
    st.markdown("This projection uses a fixed annual growth rate to simulate how your net cash flow could evolve over time. Adjust the growth rate as needed.")
    
    projection_years = list(range(0, 21))
    growth_rate = st.slider(
        "Annual Growth Rate (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.1,
        help="Select the annual growth rate (e.g., due to investments, inflation adjustments, or other factors) to apply to your net cash flow."
    ) / 100.0  # Convert percentage to decimal
    
    projected_cash_flows = [net_cash * ((1 + growth_rate) ** i) for i in projection_years]
    
    fig2, ax2 = plt.subplots()
    ax2.plot(projection_years, projected_cash_flows, marker="o", color="blue")
    ax2.set_title("Projected Net Cash Flow Over 20 Years")
    ax2.set_xlabel("Years After Retirement")
    ax2.set_ylabel("Projected Net Cash Flow ($)")
    st.pyplot(fig2)

##########################
# FERS vs CSRS Input
##########################
st.markdown("### Retirement System Type")
system_type = st.radio(
    "Select Your Retirement System:", 
    ("FERS", "CSRS"),
    help="Choose 'FERS' if you are covered under the Federal Employees Retirement System, which generally provides a defined benefit plus a TSP, or 'CSRS' if you are under the older Civil Service Retirement System. [Learn more about FERS vs. CSRS](https://www.opm.gov/retirement-services/retirement-planning/fers-vs-csrs/)"
)

# --- Compare Retirement Income Over Different Ages (VERA/DRP) ---

# Define the function for calculating retirement income
def calc_retirement_income(age: int, base_service: float, with_vera=False, with_drp=False, separation_age=50) -> float:
    """
    Calculate annual retirement income for a given age, base service,
    and scenario (VERA, DRP).
    
    :param age: The retirement age to calculate for.
    :param base_service: The user's years of federal service.
    :param with_vera: Whether VERA is applied.
    :param with_drp: Whether DRP is applied.
    :param separation_age: The age at which DRP lumpsum is applied (e.g., user final separation).
    :return: The annual retirement income for the given scenario.
    """
    # Hypothetical service
    hypothetical_service = base_service + max(0, age - current_age)
    if hypothetical_service < 0:
        hypothetical_service = 0

    # Basic pension
    pension = high3_salary * 0.01 * hypothetical_service * 0.9
    if system_type == "CSRS":
        pension = high3_salary * 0.0185 * hypothetical_service

    # SRS (FERS only if <62 & service >= 20)
    srs_amt = 0
    if system_type == "FERS" and age < 62 and hypothetical_service >= 20:
        srs_amt = srs_annual

    # TSP approximate
    hypothetical_tsp = tsp_balance * 0.04
    if age < 55 and not with_vera:
        hypothetical_tsp *= 0.90  # apply early penalty

    # DRP lumpsum as a one-time addition at separation_age
    lumpsum_drp = 0
    if with_drp and age == separation_age:
        lumpsum_drp = total_admin_leave_income

    # Annual VA disability
    va_annual = va_monthly * 12

    total_annual = pension + srs_amt + hypothetical_tsp + lumpsum_drp + va_annual
    return total_annual

# Now, generate the retirement income comparison data
min_compare_age = st.number_input("Minimum age to compare", min_value=40, max_value=80, value=50)
max_compare_age = st.number_input("Maximum age to compare", min_value=40, max_value=80, value=62)

if min_compare_age > max_compare_age:
    st.error("Error: Minimum age can't exceed maximum age.")
else:
    simulate_drp = drp_elected  # from earlier DRP checkbox
    results = []
    for age in range(int(min_compare_age), int(max_compare_age) + 1):
        normal_inc = calc_retirement_income(age, years_service, with_vera=False, with_drp=False)
        vera_inc = calc_retirement_income(age, years_service, with_vera=True, with_drp=False)
        drp_inc = calc_retirement_income(age, years_service, with_vera=False, with_drp=True, separation_age=52) if simulate_drp else 0
        
        results.append({
            "Age": age,
            "Normal": normal_inc,
            "VERA": vera_inc,
            "DRP": drp_inc
        })
    
    df_compare = pd.DataFrame(results)
    st.dataframe(df_compare.style.format("{:,.0f}"), use_container_width=True)
    
    # Create the chart with the vertical line at age 62
    fig, ax = plt.subplots()
    ax.plot(df_compare["Age"], df_compare["Normal"], label="Normal", marker="o")
    ax.plot(df_compare["Age"], df_compare["VERA"], label="VERA", marker="s", linestyle="--")
    if simulate_drp:
        ax.plot(df_compare["Age"], df_compare["DRP"], label="DRP", marker="^", linestyle=":")
    
    # Add vertical line at age 62
    ax.axvline(62, color='gray', linestyle='--', label="Age 62 – Social Security starts / SRS ends")
    
    ax.set_xlabel("Retirement Age")
    ax.set_ylabel("Approx. Annual Income ($)")
    ax.set_title(f"Retirement Income vs Age: {system_type} Normal / VERA / DRP")
    ax.legend()
    st.pyplot(fig)

# --- PDF Retirement Report Generator ---
st.markdown("### 🖨️ Download Your Personalized Retirement Report")
buffer = io.BytesIO()
p = canvas.Canvas(buffer, pagesize=letter)
width, height = letter
p.setFont("Helvetica-Bold", 16)
p.drawString(50, 750, "Retirement Summary Report")
p.line(50, 747, 550, 747)
p.setFont("Helvetica", 12)
y = 720
user_info = [
    f"Current Age: {current_age}",
    f"Years of Federal Service: {years_service}",
    f"High-3 Salary: ${high3_salary:,.2f}",
    f"TSP Balance: ${tsp_balance:,.2f}",
    f"TSP Contribution Rate: {tsp_contribution_pct}%",
    f"FEHB Plan: {health_coverage_choice} (${fehb_premium}/mo)",
    f"FEGLI Option: {fegli_option} (${fegli_premium}/mo)",
    f"Living Expenses: ${monthly_expenses:,.2f}/mo",
    f"VA Disability: ${va_monthly}/mo",
    f"Pension Type: {pension_label}",
]
for item in user_info:
    p.drawString(50, y, item)
    y -= 20
y -= 10
p.setFont("Helvetica-Bold", 12)
p.drawString(50, y, "TSP Withdrawal Details:")
p.setFont("Helvetica", 12)
y -= 20
tsp_details = [
    f"TSP Withdrawal Option: {tsp_option}",
    f"Penalty Note: {penalty_note}",
    f"Accessible TSP Balance: ${tsp_withdrawal_balance:,.2f}",
    f"Estimated Annual TSP Income: ${tsp_annual_income:,.2f}",
]
for detail in tsp_details:
    p.drawString(50, y, detail)
    y -= 20
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
p.setFont("Helvetica-Bold", 12)
p.drawString(50, y, f"📊 Total Pre-Retirement Income: ${total_preretirement_income:,.2f}")
y -= 20
p.drawString(50, y, f"🧾 Annual Expenses: ${(fegli_premium + fehb_premium + monthly_expenses) * 12:,.2f}")
y -= 20
p.drawString(50, y, f"💰 Net Cash Flow: ${net_cash:,.2f}")
y -= 30
p.setFont("Helvetica-Bold", 12)
p.drawString(50, y, "Contractor Income Analysis")
y -= 20
p.setFont("Helvetica", 12)
contractor_role = st.session_state.get("contractor_role", None)
if contractor_role:
    contractor_net_income = st.session_state.get("contractor_net_income", 0)
    contractor_gross_income = st.session_state.get("contractor_gross_income", 0)
    contractor_overhead = st.session_state.get("contractor_overhead", 0)
    srs_offset = st.session_state.get("srs_offset", 0)
    adjusted_srs = st.session_state.get("adjusted_srs", srs_annual)
    adjusted_net_cash = st.session_state.get("adjusted_net_cash", net_cash)
    p.drawString(50, y, f"Role: {contractor_role}")
    y -= 20
    p.drawString(50, y, f"Gross Income: ${contractor_gross_income:,.2f}")
    y -= 20
    p.drawString(50, y, f"Overhead: ${contractor_overhead:,.2f}")
    y -= 20
    p.drawString(50, y, f"Contractor Net Income: ${contractor_net_income:,.2f}")
    y -= 20
    p.drawString(50, y, f"SRS Reduction from Contractor Income: ${srs_offset:,.2f}")
    y -= 20
    p.drawString(50, y, f"Adjusted SRS: ${adjusted_srs:,.2f}")
    y -= 20
    p.drawString(50, y, f"Adj. Retirement Net Cash Flow: ${adjusted_net_cash:,.2f}")
    y -= 30
else:
    p.drawString(50, y, "No Contractor Data Available")
    y -= 20

# --- Additional PDF Section: Career vs. Retirement Wage Analysis ---
p.setFont("Helvetica-Bold", 12)
p.drawString(50, y, "Career vs. Retirement Wage Analysis")
y -= 20
p.setFont("Helvetica", 12)
p.drawString(50, y, f"Estimated Retirement Wage: ${estimated_retirement_wage:,.2f}")
y -= 20
p.drawString(50, y, f"Projected Continued Career Wage: ${projected_career_wage:,.2f}")
y -= 20
difference = projected_career_wage - estimated_retirement_wage
p.drawString(50, y, f"Difference: ${difference:,.2f}")
y -= 30

# --- Additional PDF Section: Pro/Con Analysis for Retirement Scenarios ---
p.setFont("Helvetica-Bold", 12)
p.drawString(50, y, "Pro/Con Analysis for Retirement Scenarios")
y -= 20
p.setFont("Helvetica", 12)
# For brevity, we print a summary note.
p.drawString(50, y, "Review the app's interactive table for detailed pros and cons based on your priorities.")
y -= 30

p.save()
buffer.seek(0)
st.download_button(
    label="📄 Download PDF Retirement Report",
    data=buffer,
    file_name="Retirement_Report.pdf",
    mime="application/pdf"
)

# --- TSP Advisor GPT Hyperlink & Footer/Disclaimer ---
st.markdown("### TSP Advisor GPT Link")
st.info("""
Welcome to your tactical TSP optimization assistant. 
Get strategic, data-backed investment advice designed for retirement-focused federal employees. 
Powered by real-world economic insight and military-grade planning discipline.
""")
advisor_url = "https://chatgpt.com/g/g-67eea2244d2c819189bee5201afec0bc-tsp-advisor-by-simforia-intelligence-group"
st.markdown(f"[**➡️ Click here to open TSP Advisor GPT**]({advisor_url})")
st.markdown("""
_If the link does not open automatically in a new tab, 
right-click and select "Open Link in New Tab."_
""")

st.markdown("---")
st.markdown("**Contact Simforia Intelligence Group**")
st.markdown(
    """
<form action="https://formspree.io/f/mzzejjkk" method="POST">
  <label>Your message:<br><textarea name="message"></textarea></label><br>
  <label>Your email (optional):<br><input type="email" name="email"></label><br>
  <button type="submit">Send</button>
</form>
""",
    unsafe_allow_html=True,
)
st.markdown(
    """
---
<small><strong>Disclaimer:</strong> This simulation tool is provided strictly for educational and informational purposes. It does not constitute official retirement guidance, legal counsel, financial advice, or tax planning. This tool is not affiliated with, endorsed by, or authorized by the Office of Personnel Management (OPM), the Department of Defense (DoD), or any federal agency. All estimates are based on simplified assumptions and publicly available retirement formulas and should not be used for final decision-making. Before acting on any output from this tool, you are strongly advised to consult your Human Resources office, a certified financial planner, tax professional, and/or retirement counselor. Use of this app constitutes acknowledgment that Simforia Intelligence Group assumes no liability for outcomes or decisions made from its use.</small>
""",
    unsafe_allow_html=True
)
