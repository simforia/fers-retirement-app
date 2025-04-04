# --- Show SRS Info (if eligible) ---
st.markdown("### 🧾 Special Retirement Supplement")
st.write(f"**SRS Eligibility:** {srs_text}")
if srs > 0:
    srs_monthly = round(srs / 12, 2)
    st.write(f"**SRS Monthly (Until Age 62):** ${srs_monthly:,.2f}")

# --- Optional Summary Export (Coming Soon Placeholder) ---
# st.download_button("📄 Export Retirement Summary (PDF)", data="Coming soon...", file_name="retirement_summary.pdf")

# --- Footer / Contact ---
st.markdown("---")
st.markdown("### 📧 Contact Simforia Intelligence Group")
st.markdown("""
If you have any questions or feedback regarding this tool, please reach out to our team securely.  
<form action="https://formspree.io/f/mzzejjkk" method="POST">
  <label>Your message:<br><textarea name="message"></textarea></label><br>
  <label>Your email (optional, for response):<br><input type="email" name="email"></label><br>
  <button type="submit">Send Feedback</button>
</form>
""", unsafe_allow_html=True)

# --- Legal Disclaimer ---
st.markdown("""
---
<small><strong>Important Notice: For Informational Purposes Only</strong><br>
This tool is intended to provide general estimates to assist federal employees in exploring early retirement options under FERS, including VERA, VSIP, and DRP.<br><br>
It is not affiliated with the U.S. Office of Personnel Management (OPM), the Department of Defense, or any federal agency. Users should consult with certified HR or financial advisors before making retirement decisions.<br><br>
By using this app, you agree that the creators are not liable for any decisions made based on the results.</small>
""", unsafe_allow_html=True)
