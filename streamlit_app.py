import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from datetime import datetime
from fpdf import FPDF
import requests

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

# 🔼 Logo and Title Top-Aligned
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
    6. Use DRP letter generator to prefill your resignation paperwork.
    """)

# ✅ Required Inputs for Eligibility Logic
current_age = st.number_input("Current Age", min_value=18, max_value=80)
years_service = st.number_input("Years of Federal Service", min_value=0, max_value=50)
drp_participation = st.selectbox("Participating in DRP?", ["", "Yes", "No"])
vsip_offer = st.number_input("VSIP Offer ($, optional)", min_value=0)
high3_salary = st.number_input("High-3 Average Salary ($)", min_value=0)
monthly_stipend = st.number_input("Monthly DRP Stipend ($, if applicable)", min_value=0)
months_on_admin_leave = st.number_input("Months on Admin Leave (1–5 typical)", min_value=0, max_value=12)
include_survivor = st.checkbox("Include Survivor Benefit Election")
survivor_reduction = 0.10 if include_survivor else 0.0
survivor_percentage = 0.5 if include_survivor else 0.0
cola_rate = st.slider("COLA Estimate (Annual % Starting at Age 62)", min_value=0.0, max_value=5.0, value=2.0, step=0.1)

# 🗪 Inject Dummy Data if Inputs Are All Zero (for preview/testing)
if all(v == 0 for v in [high3_salary, years_service, monthly_stipend, vsip_offer]):
    st.warning("🗪 Demo Mode: Using sample data for preview (update fields to see your own projection).")
    high3_salary = 90000
    years_service = 22
    monthly_stipend = 4000
    months_on_admin_leave = 4
    vsip_offer = 25000
    current_age = 56

# ✅ COLA Explanation
with st.expander("📈 What Does COLA Mean?"):
    st.markdown("Cost-of-Living Adjustments (COLA) begin at age 62 for FERS retirees and typically increase your pension annually. This slider allows you to estimate its effect.")

# 📊 Lifecycle Fund Projection (Simplified Example)
st.markdown("### 📊 Lifecycle Fund Projection (L-Fund)")
tsp_start = st.number_input("Current TSP Balance ($)", min_value=0)
tsp_growth_rate = 0.07
years_until_62 = max(62 - current_age, 0)
tsp_projected = tsp_start * ((1 + tsp_growth_rate) ** years_until_62)
st.success(f"Projected TSP at Age 62 (7% annual growth): ${tsp_projected:,.0f}")

# 🗘️ DRP Auto-Fill Letter Generator
with st.expander("✍️ Generate DRP Participation Letter"):
    user_name = st.text_input("Your Full Name")
    user_series = st.text_input("Position Title / Series / Grade")
    user_component = st.text_input("Your Duty Station or Component")

    if st.button("📄 Generate DRP Letter"):
        letter_text = f"""
Subject: Request for Participation in DRP and VERA

To Whom It May Concern,

I am writing to formally request approval to participate in the Department of Defense Deferred Resignation Program (DRP), and if eligible, retire under the Voluntary Early Retirement Authority (VERA).

I meet the eligibility criteria as defined by DoD and request written confirmation of my selection for this program. I understand participation requires a signed separation agreement and agree to exit federal service by September 30, 2025.

Thank you for your consideration.

Respectfully,

{user_name}  
{user_series}  
{user_component}
        """
        st.code(letter_text)
        st.download_button("📅 Download Letter as TXT", data=letter_text, file_name="drp_request_letter.txt")

# 📊 Safe Pie Chart Handling for Income Breakdown
values = [high3_salary, vsip_offer, monthly_stipend * months_on_admin_leave]
labels = ["High-3 Salary", "VSIP Offer", "Stipend Total"]

if values and all(v > 0 for v in values):
    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)
else:
    st.warning("⚠️ Not enough data to generate pie chart. Please enter all required fields.")
