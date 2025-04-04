
# 🧠 FERS Early Retirement Strategy Tool (DRP/VERA)

This Streamlit-based web app helps U.S. federal employees simulate early retirement outcomes under the **Federal Employees Retirement System (FERS)**. It supports DRP, VERA, and VSIP options—while providing legal strategy and red-flag detection for command interference.

---

## 🚀 Features

- 🔢 FERS pension and supplement estimator  
- 📈 TSP growth and income projections  
- 💵 Monthly income vs expenses comparison  
- 📊 10-year surplus/deficit forecast  
- 🛡️ Legal protection strategy if DRP/VERA access is denied  
- 📋 Retirement readiness checklist  
- ✍️ Letter templates for HR, IG, and OSC escalation  
- 🔄 "What-if" simulator: Retire now vs wait, DRP vs deferred annuity

---

## 🔧 How to Run

### Option 1: Local (for dev use)

```bash
pip install streamlit matplotlib
streamlit run streamlit_app.py
```

### Option 2: Streamlit Cloud

1. Push this repo to GitHub  
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)  
3. Link your GitHub repo  
4. Set `streamlit_app.py` as the launch file  
5. Click **Deploy**

---

## ✅ Required Inputs

| Field                    | Description                                  |
|--------------------------|----------------------------------------------|
| Current Age              | Your age right now                           |
| Years of Federal Service | Total creditable FERS time                   |
| High-3 Salary            | Average of your highest 3 years of pay       |
| TSP Balance              | Your Thrift Savings Plan balance             |
| Expenses & Mortgage      | Household + debt info for budgeting          |
| Cash Reserves            | Emergency fund or savings                    |
| VSIP Offer               | Buyout amount (optional)                     |
| DRP Participation        | Yes/No toggle                                |

---

## ⚖️ Legal Strategy Engine

Includes safeguards and references for:
- 10 U.S.C. §129a – Mission Impact Analysis
- 5 U.S.C. §2302 – Prohibited Personnel Practices
- 5 CFR §842 Subpart G – VERA eligibility
- DoD DRP Directive (April 2025)

---

## 🛡️ If Management Interferes…

We built in escalation logic. You’ll get:
- Formal challenge letters
- Red flag alerts
- MSPB/IG/OSC complaint templates
