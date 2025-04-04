import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from datetime import datetime

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
st.markdown("<h2 style='text-align: center;'>🧠 Simforia Intelligence Group</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'><em>Retirement Optimization Toolkit – DRP / VERA / TSP Strategy Suite</em></p>", unsafe_allow_html=True)
st.image("simforia_logo.png", width=150)

# 📘 Instructions
with st.expander("ℹ️ How to Use This Tool"):
    st.markdown("""
    1. Enter your current age and total federal service.
    2. Select whether you are participating in DRP.
    3. Review your eligibility and key deadlines.
    4. Use the GPT link at the bottom for deeper retirement strategy questions.
    5. This tool tracks anonymous visits to help improve performance (local only).
    """)

# ✅ Required Inputs for Eligibility Logic
current_age = st.number_input("Current Age", min_value=18, max_value=80)
years_service = st.number_input("Years of Federal Service", min_value=0, max_value=50)
drp_participation = st.selectbox("Participating in DRP?", ["", "Yes", "No"])
vsip_offer = st.number_input("VSIP Offer ($, optional)", min_value=0)
high3_salary = st.number_input("High-3 Average Salary ($)", min_value=0)

with st.expander("📢 Official DRP & VERA Guidance – Click to View"):
    st.markdown("""
**📅 Key Dates:**
- DRP Election Window: **April 7–14, 2025**
- Admin Leave Begins: **May 1, 2025**
- Resignation/Retirement Deadline: **September 30, 2025**
- No DRP-based extension beyond **December 31, 2025**

**📌 Eligibility Highlights:**
- Must sign a **written agreement** before entering admin leave
- DRP is **not available** to:
  - Non-Appropriated Fund employees
  - Foreign Local Nationals
  - Dual-Status Military Technicians
  - Highly Qualified Experts
  - Re-employed Annuitants
- Probationary employees **are** eligible

**📣 Authority & Oversight:**
- Exemptions must be documented under **10 U.S.C. §129a**
- Mission-critical exemptions require approval by PSA or CJCS

**📍 Local Note (Tobyhanna Army Depot):**
- Eligibility guidance pending from DA / AMC / CECOM
- DO NOT contact Resource Management with DRP questions until official guidance is released
- Questions? Contact Army Benefits Center – Civilian: 
  - 📧 usarmy.riley.chra-hqs.mbx.abc-c-amc@army.mil  
  - 📞 877-276-9287 or 571-644-6041 (Mon–Thurs, 0800–1600 CST)
""")

# ⏳ Real-Time Countdown to DRP Election Deadline
deadline = datetime(2025, 4, 14)
today = datetime.today()
days_left = (deadline - today).days

if days_left > 0:
    st.info(f"📆 {days_left} days left until DRP Election Deadline (April 14, 2025)")
else:
    st.warning("🚫 DRP Election window is closed or deadline has passed.")

# ✅ Quick Eligibility Checklist
st.markdown("### ✅ DRP / VERA Eligibility Checklist")
eligible = True

if current_age < 50 and years_service < 25:
    st.error("❌ You must be age 50 with at least 20 years of service, or have 25+ years at any age.")
    eligible = False
elif current_age >= 50 and years_service >= 20:
    st.success("✔️ Age 50+ with 20+ years: Meets minimum for VERA eligibility.")
elif years_service >= 25:
    st.success("✔️ 25+ years of service at any age: Meets eligibility.")
else:
    st.warning("⚠️ Unclear eligibility — check with HR or ABC-C to confirm.")

if drp_participation == "Yes":
    st.markdown("✔️ Selected DRP participation")
    st.markdown("✔️ Must sign written agreement before May 1, 2025")
    st.markdown("✔️ Must separate no later than September 30, 2025")

# 💸 Pension Estimator
st.markdown("### 💰 Pension Estimate")
pension = 0.01 * high3_salary * years_service
st.info(f"Estimated FERS Annual Pension: ${pension:,.0f}")

# 💵 VSIP Display
if vsip_offer > 0:
    st.success(f"VSIP Incentive Payment (Taxable): ${vsip_offer:,.0f}")

# 💬 GPT Advisor Link
st.markdown("---")
st.markdown("### 💬 Have Questions About TSP, DRP, or VERA?")
st.markdown("[🧠 Ask Simforia’s TSP Advisor GPT](https://chat.openai.com/g/g-67eea2244d2c819189bee5201afec0bc-tsp-advisor-by-simforia-intellegence-group) →")
