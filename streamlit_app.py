import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from datetime import datetime
from fpdf import FPDF

# 🔍 Page Tracking for Metrics (Session ID)
st.session_state.setdefault("visits", 0)
st.session_state.visits += 1

# 📐 Increase Global Font Size
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-size: 18px !important;
        }
    </style>
""", unsafe_allow_html=True)

# 🖼️ Logo and Title Top-Aligned
st.markdown("<h2 style='text-align: center;'> Simforia Intelligence Group</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'><em>Retirement Optimization Toolkit – DRP / VERA / TSP Strategy Suite</em></p>", unsafe_allow_html=True)
st.image("simforia_logo.png", width=150)

# 📘 Instructions
with st.expander("ℹ️ How to Use This Tool"):
    st.markdown("""
    1. Enter your current age and total federal service.
    2. Select whether you are participating in DRP.
    3. Review your eligibility and key deadlines.
    4. Use the GPT link at the bottom for deep TSP insight.
    5. Generate a retirement report with projections and legal defenses.
    """)

# ✅ Required Inputs for Eligibility Logic
current_age = st.number_input("Current Age", min_value=18, max_value=80)
years_service = st.number_input("Years of Federal Service", min_value=0, max_value=50)
drp_participation = st.selectbox("Participating in DRP?", ["", "Yes", "No"])
vsip_offer = st.number_input("VSIP Offer ($, optional)", min_value=0)
high3_salary = st.number_input("High-3 Average Salary ($)", min_value=0)
monthly_stipend = st.number_input("Monthly DRP Stipend ($, if applicable)", min_value=0)
months_on_admin_leave = st.number_input("Months on Admin Leave (1–5 typical)", min_value=0, max_value=12)

with st.expander("📢 Official DRP & VERA Guidance – Click to View"):
    st.markdown("""
**📅 Key Dates:**
- DRP Election Window: April 7–14, 2025
- Admin Leave Begins: May 1, 2025
- Resignation/Retirement Deadline: September 30, 2025

**Eligibility:**
- DRP/VERA available to eligible employees
- Exemptions must follow 10 U.S.C. §129a (mission-critical criteria)

**Lawful Restrictions:**
- 5 U.S.C. §2302: Prohibited personnel practices (including retaliation)
- CJCS/PSA concurrence required for exemptions from DRP
""")

# ⏳ Real-Time Countdown to DRP Election Deadline
deadline = datetime(2025, 4, 14)
today = datetime.today()
days_left = (deadline - today).days

if days_left > 0:
    st.info(f"📆 {days_left} days left until DRP Election Deadline (April 14, 2025)")
else:
    st.warning("🚫 DRP Election window is closed or deadline has passed.")

# 💸 Pension + Supplement + VSIP Breakdown
st.markdown("### 💰 Retirement Income Breakdown")
pension = 0.01 * high3_salary * years_service
fers_supplement = 25 * years_service * 12
stipend_total = monthly_stipend * months_on_admin_leave

st.info(f"FERS Annual Pension: ${pension:,.0f}")
st.info(f"FERS Supplement (until age 62): ${fers_supplement:,.0f}/yr")

if vsip_offer > 0:
    st.success(f"VSIP Incentive (Taxable): ${vsip_offer:,.0f}")
if stipend_total > 0:
    st.info(f"DRP Admin Leave Stipend (Total): ${stipend_total:,.0f}")

retirement_total = pension + fers_supplement + vsip_offer
st.markdown(f"### 🧮 Estimated Income Excluding DRP Stipend: **${retirement_total:,.0f}**")

# 📊 Charts
st.markdown("### 📈 Visualized Retirement Breakdown")
labels = ['Pension', 'Supplement', 'VSIP']
values = [pension, fers_supplement, vsip_offer]

fig1, ax1 = plt.subplots()
ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
ax1.axis('equal')
st.pyplot(fig1)

# 📊 Stacked Bar Projection (10-Year Outlook)
years = list(range(1, 11))
pension_10yr = [pension] * 10
supplement_10yr = [fers_supplement if current_age + i < 62 else 0 for i in range(10)]
vsip_10yr = [vsip_offer] + [0] * 9

data = pd.DataFrame({
    "Year": years,
    "Pension": pension_10yr,
    "Supplement": supplement_10yr,
    "VSIP": vsip_10yr
})

data.set_index("Year", inplace=True)
fig2, ax2 = plt.subplots()
data.plot(kind="bar", stacked=True, ax=ax2)
ax2.set_title("10-Year Income Projection")
ax2.set_ylabel("Annual $")
ax2.legend(loc='upper right')
st.pyplot(fig2)

# 📤 PDF Report Export
if st.button("📥 Generate PDF Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Simforia DRP / VERA Strategy Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Pension: ${pension:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"FERS Supplement: ${fers_supplement:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"VSIP: ${vsip_offer:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"Admin Leave Stipend: ${stipend_total:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"10-Year Estimated Value (excl. stipend): ${retirement_total * 10:,.0f}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt="Key Policy:\n- 10 U.S.C. §129a: Mission-critical exemption rules\n- 5 U.S.C. §2302: Prohibited personnel practices including coercion or retaliation")

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    st.download_button("📄 Download Report as PDF", data=pdf_output.getvalue(), file_name="simforia_retirement_report.pdf", mime="application/pdf")

# 🗣️ Feedback Form and Logging
st.markdown("---")
st.markdown("### 📥 Submit Feedback or Report Issues")
with st.form("feedback_form"):
    feedback_type = st.selectbox("Type of Feedback", ["General", "Bug Report", "Feature Request", "Policy Clarification", "Other"])
    feedback_text = st.text_area("Let us know if something is wrong or you'd like to suggest a feature:")
    submitted = st.form_submit_button("Submit Feedback")
    if submitted:
        response = requests.post(
            "https://formspree.io/f/mzzejjkk",
            data={"type": feedback_type, "message": feedback_text}
        )
        if response.status_code == 200:
            st.success("✅ Feedback submitted securely. We'll follow up if needed.")
        else:
            st.error("⚠️ There was a problem submitting your feedback. Please try again.")

st.markdown("---")
st.markdown("### 💬 Have Questions About TSP, DRP, or VERA?")
st.markdown("[🧠 Ask Simforia’s TSP Advisor GPT — Comprehensive TSP Strategy and Projections](https://chat.openai.com/g/g-67eea2244d2c819189bee5201afec0bc-tsp-advisor-by-simforia-intellegence-group) →")

# 📫 Contact for Support or Feedback
st.markdown("---")
st.markdown("### 📫 Contact Simforia Intelligence Group
If you're unable to use the form above or need direct assistance, please use our secure contact portal by submitting feedback above. For verified inquiries, contact will be initiated on our side. (Email address intentionally withheld to prevent bot scraping.)
