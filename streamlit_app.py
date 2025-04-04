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

