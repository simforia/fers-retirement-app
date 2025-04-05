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

# --- Header ---
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
    """
    )

# --- Inputs ---
current_age = st.number_input("Current Age", min_value=18, max_value=80)
years_service = st.number_input("Years of Federal Service", min_value=0, max_value=50)
high3_salary = st.number_input("High-3 Average Salary ($)", min_value=0)
tsp_balance = st.number_input("Current TSP Balance ($)", min_value=0)
tsp_contribution_pct = st.slider("TSP Contribution (% of Salary)", 0, 100, 5)
tsp_contribution_annual = high3_salary * (tsp_contribution_pct / 100)

# --- TSP Withdrawal Calculation (For VERA Retirement) ---
st.markdown("### TSP Withdrawal Calculation (For VERA Retirement)")
tsp_option = st.radio(
    "Select TSP Withdrawal Option:",
    (
        "Withdraw now (penalty applies if under 55)",
        "Delay withdrawal until 59½ (No withdrawal now)",
        "Set up SEPP plan",
    ),
)
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
# Assume a 4% annual withdrawal rate on the accessible TSP balance.
tsp_annual_income = tsp_withdrawal_balance * 0.04
st.markdown(f"**Estimated Annual TSP Income:** ${tsp_annual_income:,.2f}")

# --- FEHB / CHAMPVA & FEGLI Selection ---
st.markdown("### FEHB / CHAMPVA & FEGLI Selection")
health_coverage_choice = st.radio(
    "Select your primary health coverage:",
    ("None", "FEHB", "CHAMPVA")
)

if health_coverage_choice == "None":
    fehb_premium = 0
    st.markdown("No primary coverage selected. Make sure this matches your real situation.")
elif health_coverage_choice == "FEHB":
    # If user selects FEHB, let them pick a plan
    fehb_plan = st.selectbox("FEHB Plan Type", ["Self Only", "Self + One", "Family"])
    fehb_costs = {"Self Only": 300, "Self + One": 550, "Family": 750}
    fehb_premium = fehb_costs[fehb_plan]
    st.markdown(f"**Selected FEHB Plan:** {fehb_plan}, Monthly Premium = ${fehb_premium}")
elif health_coverage_choice == "CHAMPVA":
    fehb_premium = 0  # For simulation: No FEHB cost if using CHAMPVA
    st.markdown(
        """
    **CHAMPVA** (Civilian Health and Medical Program of the Department of Veterans Affairs)
    is a comprehensive health care benefits program in which the VA shares the cost of covered
    health care services and supplies with eligible beneficiaries (e.g., spouse/child of a vet
    rated permanently & totally disabled, or survivors of a vet who died from a service-related
    disability). 
    
    For more information, see the official [CHAMPVA Program page](https://www.va.gov/COMMUNITYCARE/programs/dependents/champva/).
    """
    )
    st.markdown("No additional monthly premium is assumed here for demonstration.")

# FEGLI Option
fegli_option = st.selectbox("FEGLI Option", ["None", "Basic", "Basic + Option A", "Basic + Option B"])
fegli_costs = {"None": 0, "Basic": 50, "Basic + Option A": 70, "Basic + Option B": 90}
fegli_premium = fegli_costs[fegli_option]

# Other living expenses input
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
    st.markdown(
        f"High-3 Salary * 1% * Years of Service * 0.9 = {high3_salary} * 0.01 * {years_service} * 0.9 = ${fers_regular:,.2f}"
    )
    st.markdown("**Disability FERS Pension Calculation:**")
    st.markdown(
        f"High-3 Salary * (0.6 if {current_age} < 62 else 0.4) = {high3_salary} * (0.6) = ${fers_disability:,.2f}"
    )

# --- What-if Comparison ---
st.markdown("### 🧮 What-if Comparison: Disability vs. Regular Retirement")
comparison_data = {
    "Scenario": ["Regular FERS Retirement", "Disability Retirement"],
    "Annual Pension ($)": [fers_regular, fers_disability],
    "Monthly Pension ($)": [monthly_regular, monthly_disability],
    "SRS Eligible": ["Yes" if srs > 0 else "No"] * 2,
    "VA Monthly Added ($)": [va_monthly] * 2,
    "FEHB/FEGLI Annual Cost ($)": [(fegli_premium + fehb_premium) * 12] * 2,
}
comp_df = pd.DataFrame(comparison_data)
comp_df = comp_df.style.format(
    {
        "Annual Pension ($)": "${:,.2f}",
        "Monthly Pension ($)": "${:,.2f}",
        "VA Monthly Added ($)": "${:,.2f}",
        "FEHB/FEGLI Annual Cost ($)": "${:,.2f}",
    }
)
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
    "Amount ($)": income_values,
}
summary_df = pd.DataFrame(summary_data)
total_preretirement_income = sum(income_values)

st.dataframe(summary_df.style.format({"Amount ($)": "${:,.2f}"}), use_container_width=True)
st.success(f"**Combined Pre-Retirement Income:** ${total_preretirement_income:,.2f}")

# --- Net Cash After Expenses ---
total_expenses = (fegli_premium + fehb_premium + monthly_expenses) * 12
net_cash = total_preretirement_income - total_expenses
st.markdown("### 💰 Net Cash After Expenses")
st.info(f"**Annual Expenses (FEHB + FEGLI + Living):** ${total_expenses:,.2f}")
if net_cash >= 0:
    st.success(f"**Net Cash Flow:** ${net_cash:,.2f}")
else:
    st.error(f"**Net Cash Flow:** ${net_cash:,.2f}")

# --- Contractor Toolkit Section with SRS Earnings Test ---
with st.expander("🛠 Contractor Toolkit (SRS Impact)"):
    st.markdown("### Contractor Income Analysis & SRS Earnings Test")

    contractor_role = st.text_input("Contractor Role", "Federal Compliance Consultant")
    hourly_rate = st.number_input("Hourly Rate ($)", min_value=0, value=120)
    hours_per_week = st.number_input("Hours per Week", min_value=0, value=25)
    weekly_overhead = st.number_input("Weekly Overhead Costs ($)", min_value=0, value=200)

    annual_gross = hourly_rate * hours_per_week * 52
    annual_overhead = weekly_overhead * 52
    contractor_net_income = annual_gross - annual_overhead

    st.markdown(f"**Annual Gross Contractor Income:** ${annual_gross:,.2f}")
    st.markdown(f"**Annual Overhead Costs:** ${annual_overhead:,.2f}")
    if contractor_net_income >= 0:
        st.success(f"**Net Contractor Income:** ${contractor_net_income:,.2f}")
    else:
        st.error(f"**Net Contractor Income:** ${contractor_net_income:,.2f}")

    # SRS Earnings Test
    apply_srs_earnings_test = st.checkbox("Apply FERS SRS earnings test to contractor income?")
    earnings_test_threshold = 21240  # Example threshold

    srs_offset = 0
    adjusted_srs = srs_annual  # Start with no offset
    if apply_srs_earnings_test and srs_annual > 0:
        if contractor_net_income > earnings_test_threshold:
            over_threshold = contractor_net_income - earnings_test_threshold
            # $1 SRS reduction for every $2 above threshold
            srs_offset = over_threshold / 2
        adjusted_srs = max(0, srs_annual - srs_offset)

        st.markdown("---")
        st.markdown(f"**Original SRS:** ${srs_annual:,.2f}")
        st.markdown(f"**Earnings Test Threshold:** ${earnings_test_threshold:,.2f}")
        st.markdown(f"**SRS Reduction Due to Contractor Income:** ${srs_offset:,.2f}")
        st.markdown(f"**Adjusted SRS:** ${adjusted_srs:,.2f}")

    srs_delta = adjusted_srs - srs_annual
    adjusted_retirement_income = total_preretirement_income + srs_delta
    adjusted_net_cash = adjusted_retirement_income - total_expenses

    if apply_srs_earnings_test and srs_offset > 0:
        st.info(f"**Adjusted Retirement Net Cash Flow (with SRS reduction): ${adjusted_net_cash:,.2f}**")
    else:
        st.info(f"**Retirement Net Cash Flow (unchanged): ${adjusted_net_cash:,.2f}**")

    # Compare adjusted retirement net cash flow vs. contractor net income
    st.markdown("### Comparison: Adjusted Retirement vs. Contractor Income")
    incomes = {
        "Retirement Net Cash (Adj.)": adjusted_net_cash,
        "Contractor Net Income": contractor_net_income,
    }
    comp_df2 = pd.DataFrame(list(incomes.items()), columns=["Income Source", "Amount"])

    import matplotlib.pyplot as plt
    fig3, ax3 = plt.subplots()
    colors = ["green" if adjusted_net_cash >= 0 else "red", "blue"]
    ax3.bar(comp_df2["Income Source"], comp_df2["Amount"], color=colors)
    ax3.set_ylabel("Amount ($)")
    ax3.set_title("Income Comparison: Adj. Retirement vs. Contractor")
    st.pyplot(fig3)

    # Save contractor & offset data for CSV/PDF
    st.session_state["contractor_role"] = contractor_role
    st.session_state["contractor_net_income"] = contractor_net_income
    st.session_state["contractor_gross_income"] = annual_gross
    st.session_state["contractor_overhead"] = annual_overhead
    st.session_state["srs_offset"] = srs_offset
    st.session_state["adjusted_srs"] = adjusted_srs
    st.session_state["adjusted_retirement_income"] = adjusted_retirement_income
    st.session_state["adjusted_net_cash"] = adjusted_net_cash

# --- Federal Independent Contractor Steps ---
with st.expander("🧷 Federal Independent Contractor Steps"):
    st.markdown(
        """
    **1. Determine Your Small Business Status**  
    - Review the [SBA Table of Size Standards](https://www.sba.gov/document/support--table-size-standards) to see whether you qualify as a small business.

    **2. Identify Your NAICS Code**  
    - Match your products/services to the correct [NAICS code](https://www.census.gov/naics/).

    **3. Set Up Your Business Entity**  
    - Obtain a federal business tax ID (EIN) if needed  
    - Register your business name with the state  
    - **LLC (Limited Liability Company):** 
      - Provides liability protection of a corporation with the tax efficiencies/flexibility of a partnership.
      - Profits and losses “pass through” to members unless you choose to be taxed as an S-corp or C-corp.
    - **S-corporation (S-corp):**
      - A tax election made by an LLC or a corporation that passes corporate income, losses, and deductions through to shareholders.
      - Limits on the number and type of shareholders (generally must be U.S. citizens or permanent residents).
      - Avoids corporate-level taxation but must follow strict IRS rules.
    - **C-corporation (C-corp):**
      - A standard corporate entity whose profits are taxed at the corporate level.
      - Potential for double taxation (company & shareholders).
      - No shareholder restrictions; can issue multiple classes of stock.

    **4. Register in the System for Award Management (SAM)**  
    - Mandatory for doing business with the Federal Government: [SAM.gov](https://sam.gov/).

    **5. Explore Contract Opportunities**  
    - Check [SAM.gov](https://sam.gov/) for prime contract solicitations.
    - Consider subcontracting with established federal contractors.

    ---
    **Disclaimer:** Requirements vary by industry and agency. Seek professional help for legal/tax compliance. This overview is for informational purposes only and does not replace professional guidance.
    """
    )

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
            # Contractor data
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
            # Contractor data from session state
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

# --- Sensitivity Analysis: Net Cash Flow vs. Years of Service ---
with st.expander("🔍 Sensitivity Analysis: Net Cash Flow vs. Years of Service"):
    years_range = list(range(0, 51))
    net_cash_sensitivity = []
    for y in years_range:
        # For simplicity, recalc a theoretical pension based on y years of service.
        pension_value = high3_salary * 0.01 * y * 0.9
        total_income = vsip_amount + pension_value
        total_exp = (fegli_premium + fehb_premium + monthly_expenses) * 12
        net_cash_sensitivity.append(total_income - total_exp)
    fig, ax = plt.subplots()
    ax.plot(years_range, net_cash_sensitivity, marker="o")
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
    ax2.plot(projection_years, projected_cash_flows, marker="o", color="blue")
    ax2.set_title("Projected Net Cash Flow Over 20 Years")
    ax2.set_xlabel("Years After Retirement")
    ax2.set_ylabel("Projected Net Cash Flow ($)")
    st.pyplot(fig2)

# --- Compare Retirement Income Over Different Ages (VERA/DRP) ---
with st.expander("📊 Compare Retirement Income Over Different Ages (VERA/DRP)"):
    st.markdown("""
    This section will estimate your approximate **annual retirement income** at each 
    retirement age in a user-selected range, for different scenarios:
    
    - **Normal** (no VERA, no DRP)
    - **VERA** (if age ≥ 50 and you have enough service to qualify)
    - **DRP** (adds an admin leave or lump sum if DRP is elected)
    
    **Note:** This is a naive illustration. In production, refine the 
    calculations to reflect actual TSP penalty rules, 
    early retirement reductions, and DRP admin leave details.
    """)

    min_compare_age = st.number_input("Minimum age to compare", min_value=40, max_value=80, value=50)
    max_compare_age = st.number_input("Maximum age to compare", min_value=40, max_value=80, value=62)

    if min_compare_age > max_compare_age:
        st.error("Error: Minimum age can't exceed maximum age.")
    else:
        # We'll check if DRP is relevant from user input
        simulate_drp = drp_elected

        def calc_retirement_income(age: int, service: float, with_vera=False, with_drp=False) -> float:
            """
            Returns approximate annual retirement income 
            (pension + TSP + SRS if applicable) for the given scenario.
            
            This is a naive example. You can refine or replace it with 
            your actual early retirement logic, TSP penalty logic, etc.
            """

            # 1) Hypothetical service if the user works until 'age'
            hypothetical_service = service + (age - current_age if age > current_age else 0)
            if hypothetical_service < 0:
                hypothetical_service = 0

            # 2) Basic pension formula
            hypothetical_pension = high3_salary * 0.01 * hypothetical_service * 0.9

            # 3) SRS if <62 and >=20 yrs
            hypothetical_srs = 0.0
            if (age < 62) and (hypothetical_service >= 20):
                hypothetical_srs = srs_annual

            # 4) TSP approximate. If age < 55 => 10% penalty unless with_vera
            hypothetical_tsp = tsp_balance * 0.04
            if age < 55 and not with_vera:
                hypothetical_tsp *= 0.90  # naive penalty approach

            # 5) If with_vera => check eligibility
            if with_vera:
                # For demonstration: if (age>=50 & service>=20) or (service>=25) => apply VERA
                if (age >= 50 and hypothetical_service >= 20) or (hypothetical_service >= 25):
                    # Suppose we do a naive 2% penalty/year under 55 -> skip for brevity
                    if age < 55:
                        hypothetical_pension *= 0.90  # e.g. 10% reduction
                    # TSP might be penalty-free with VERA
                else:
                    # If not truly eligible
                    with_vera = False  # fallback to normal

            # 6) DRP lumpsum
            lumpsum_drp = 0.0
            if with_drp:
                lumpsum_drp = total_admin_leave_income  # from earlier DRP slider

            total_annual = hypothetical_pension + hypothetical_srs + hypothetical_tsp + lumpsum_drp
            return total_annual

        results = []
        for a in range(int(min_compare_age), int(max_compare_age) + 1):
            normal_inc = calc_retirement_income(age=a, service=years_service, with_vera=False, with_drp=False)
            vera_inc = calc_retirement_income(age=a, service=years_service, with_vera=True, with_drp=False)
            drp_inc = 0.0
            if simulate_drp:
                drp_inc = calc_retirement_income(age=a, service=years_service, with_vera=False, with_drp=True)

            results.append({
                "Age": a,
                "Normal": normal_inc,
                "VERA": vera_inc,
                "DRP": drp_inc,
            })

        df_compare = pd.DataFrame(results)
        st.markdown("#### Retirement Income by Age & Scenario")
        st.dataframe(df_compare.style.format("{:,.2f}"), use_container_width=True)

        # Plot
        st.markdown("_Naive calculations for demonstration; refine these for real logic._")

        fig_compare, ax_compare = plt.subplots()
        ax_compare.plot(df_compare["Age"], df_compare["Normal"], marker='o', label="Normal")
        ax_compare.plot(df_compare["Age"], df_compare["VERA"], marker='o', label="VERA")
        if simulate_drp:
            ax_compare.plot(df_compare["Age"], df_compare["DRP"], marker='o', label="DRP")

        ax_compare.set_xlabel("Retirement Age")
        ax_compare.set_ylabel("Approx. Annual Income ($)")
        ax_compare.set_title("Retirement Income vs. Age: Normal / VERA / DRP")
        ax_compare.legend()
        st.pyplot(fig_compare)

# --- PDF Retirement Report Generator ---
st.markdown("### 🖨️ Download Your Personalized Retirement Report")
buffer = io.BytesIO()
p = canvas.Canvas(buffer, pagesize=letter)
width, height = letter

# Header
p.setFont("Helvetica-Bold", 16)
p.drawString(50, 750, "Retirement Summary Report")
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
    f"FEHB Plan: {health_coverage_choice} (${fehb_premium}/mo)",
    f"FEGLI Option: {fegli_option} (${fegli_premium}/mo)",
    f"Living Expenses: ${monthly_expenses:,.2f}/mo",
    f"VA Disability: ${va_monthly}/mo",
    f"Pension Type: {pension_label}",
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
    f"Estimated Annual TSP Income: ${tsp_annual_income:,.2f}",
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
p.drawString(50, y, f"🧾 Annual Expenses: ${(fegli_premium + fehb_premium + monthly_expenses) * 12:,.2f}")
y -= 20
p.drawString(50, y, f"💰 Net Cash Flow: ${net_cash:,.2f}")
y -= 30

# Optional: horizontal line to separate totals from contractor
# p.line(50, y, 550, y)
# y -= 10

# --- New Contractor Section ---
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
<small><strong>Disclaimer:</strong> This simulation tool is provided strictly for educational and informational purposes. It does not constitute official retirement guidance, legal counsel, financial advice, or tax planning. This tool is not affiliated with, endorsed by, or authorized by the Office of Personnel Management (OPM), the Department of Defense (DoD), or any federal agency. All estimates are based on simplified assumptions and publicly available retirement formulas and should not be used for final decision-making. Individual circumstances, benefit eligibility, agency-specific policies, and future changes to law or policy may significantly alter results. Before acting on any output from this tool, you are strongly advised to consult your Human Resources office, a certified financial planner, tax professional, and/or retirement counselor. Use of this app constitutes acknowledgment that Simforia Intelligence Group assumes no liability for outcomes or decisions made from its use.</small>
""",
    unsafe_allow_html=True
)
