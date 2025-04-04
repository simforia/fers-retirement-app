import streamlit as st
from datetime import datetime
from fpdf import FPDF

# 🔍 Page Tracking for Metrics (Session ID)
st.session_state.setdefault("visits", 0)
st.session_state.visits += 1

# 📊 Increase Global Font Size
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-size: 18px !important;
        }
    </style>
""", unsafe_allow_html=True)

# 🔼 Logo Top-Left and Title Centered
logo_and_title = """
<div style="display: flex; align-items: center; justify-content: space-between;">
    <img src="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/simforia_logo.png" alt="Simforia Logo" style="height: 60px;">
    <div style="flex-grow: 1; text-align: center;">
        <h2>Simforia Intelligence Group</h2>
        <p style='font-size: 18px;'><em>Retirement Optimization Toolkit – DRP / VERA / TSP Strategy Suite</em></p>
    </div>
</div>
"""
st.markdown(logo_and_title, unsafe_allow_html=True)

# 📘 Instructions
with st.expander("ℹ️ How to Use This Tool"):
    st.markdown("""
    1. Enter your current age and total federal service.
    2. Select whether you are participating in DRP.
    3. Review your eligibility and key deadlines.
    4. Use the GPT link at the bottom for deeper TSP insights.
    5. Generate a DRP participation letter.
    """)

# ✅ Required Inputs for Eligibility Logic
current_age = st.number_input("Current Age", min_value=18, max_value=80)
years_service = st.number_input("Years of Federal Service", min_value=0, max_value=50)
drp_participation = st.selectbox("Participating in DRP?", ["", "Yes", "No"])
vsip_offer = st.number_input("VSIP Offer ($, optional)", min_value=0)
high3_salary = st.number_input("High-3 Average Salary ($)", min_value=0)

include_survivor = st.checkbox("Include Survivor Benefit Election")
survivor_reduction = 0.10 if include_survivor else 0.0
survivor_percentage = 0.5 if include_survivor else 0.0

cola_rate = st.slider("COLA Estimate (Annual % Starting at Age 62)", min_value=0.0, max_value=5.0, value=2.0, step=0.1)

# 🔘️ DRP Auto-Fill Letter Generator
with st.expander("✍️ Generate DRP Participation Letter"):
    user_name = st.text_input("Your Full Name")
    user_series = st.text_input("Position Title / Series / Grade")
    user_component = st.text_input("Your Duty Station or Component")

    if st.button("🔕️ Generate DRP Letter"):
        letter_text = f"""
Subject: Formal Request for Participation in DRP and VERA

To Whom It May Concern,

I am writing to formally request approval for my participation in the Department of Defense Deferred Resignation Program (DRP), and if eligible, to retire under the Voluntary Early Retirement Authority (VERA). I meet the eligibility criteria as defined by DoD guidelines, and I am fully prepared to comply with all required procedures.

As per the terms, I understand that my participation requires a signed separation agreement, and I agree to exit federal service by September 30, 2025. I request written confirmation of my selection for this program at your earliest convenience.

I appreciate your attention to this matter, and I look forward to your confirmation.

Sincerely,

{user_name}
{user_series}
{user_component}
        """
        st.code(letter_text)
        st.download_button("🔕️ Download Letter as TXT", data=letter_text, file_name="drp_request_letter.txt")

# 🔗 GPT Link for TSP / DRP / VERA Q&A
st.markdown("---")
st.markdown("### 💬 Have Questions About TSP, DRP, or VERA?")
st.markdown("[🧠 Ask Simforia’s TSP Advisor GPT — Comprehensive TSP Strategy and Projections](https://chat.openai.com/g/g-67eea2244d2c819189bee5201afec0bc-tsp-advisor-by-simforia-intellegence-group) →")

# 📝 Provide Contact Information for Feedback
st.markdown("### 📧 Contact Simforia Intelligence Group")
st.markdown("""
If you have any questions or feedback regarding the tool, please reach out to our team securely. 
<form action="https://formspree.io/f/mzzejjkk" method="POST">
  <label>Your message:<br><textarea name="message"></textarea></label><br>
  <label>Your email (optional, for response):<br><input type="email" name="email"></label><br>
  <button type="submit">Send Feedback</button>
</form>
""", unsafe_allow_html=True)
