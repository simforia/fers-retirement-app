
import streamlit as st
import matplotlib.pyplot as plt

# Title
st.title("FERS Early Retirement Strategy Tool (DRP & VERA)")

st.markdown("This tool helps federal employees plan early retirement with DRP, VERA, and VSIP options. Input your data below:")

# User Inputs
age = st.number_input("Current Age", min_value=18, max_value=80, step=1)
years_service = st.number_input("Years of Federal Service", min_value=1, max_value=50, step=1)
high3_salary = st.number_input("High-3 Salary ($)", min_value=0)
tsp_balance = st.number_input("Current TSP Balance ($)", min_value=0)
monthly_expenses = st.number_input("Monthly Household Expenses ($)", min_value=0)
mortgage_remaining = st.number_input("Remaining Mortgage Balance ($)", min_value=0)
mortgage_payment = st.number_input("Monthly Mortgage Payment ($)", min_value=0)
cash_reserves = st.number_input("Cash Reserves ($)", min_value=0)
spouse_income = st.number_input("Spouse Income ($/yr)", min_value=0)
vsip_offer = st.number_input("VSIP Offer ($)", min_value=0)
drp_participation = st.selectbox("Participating in DRP?", ["Yes", "No"])
deferred_annuity_age = st.number_input("Deferred Annuity Age (if DRP)", min_value=age, max_value=80, value=62)

# Calculate pension and FERS supplement
pension = 0.01 * high3_salary * years_service
fers_supplement = 25 * years_service if age < 62 else 0

# Simple forecast
monthly_pension = pension / 12
monthly_income = monthly_pension + fers_supplement + (spouse_income / 12)

# Results
st.header("Estimated Monthly Retirement Income")
st.write(f"Pension: ${monthly_pension:,.2f}")
st.write(f"FERS Supplement: ${fers_supplement:,.2f}")
st.write(f"Total Monthly Income (inc. spouse): ${monthly_income:,.2f}")
st.write(f"Monthly Expenses: ${monthly_expenses:,.2f}")
net_surplus = monthly_income - monthly_expenses
st.write(f"**Monthly Surplus/Deficit:** ${net_surplus:,.2f}")

# Chart
st.header("10-Year Surplus/Deficit Forecast")
years = list(range(1, 11))
net_cash = [cash_reserves + (net_surplus * 12 * y) for y in years]

fig, ax = plt.subplots()
ax.plot(years, net_cash, marker='o')
ax.set_title("10-Year Financial Forecast")
ax.set_xlabel("Years After Retirement")
ax.set_ylabel("Projected Surplus ($)")
st.pyplot(fig)

st.markdown("All figures are estimates. For legal protections, escalation letters, and DRP/VERA defense tactics, consult the strategy section.")
