import os
import sys
import json
import time
import hmac

from dotenv import load_dotenv
from pydantic import BaseModel

import pandas as pd
import streamlit as st
from google import genai

# ==========================================================
# CLOUD / LOCAL CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="🤖 AI Sales CRM",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()


def get_setting(name):
    """Read local .env variables or securely hosted Streamlit secrets."""
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name)
    except (FileNotFoundError, OSError):
        return None
    except Exception:
        # Streamlit raises StreamlitSecretNotFoundError if no secrets exist.
        return None


API_KEY = get_setting("GEMINI_API_KEY")
APP_PASSWORD = get_setting("APP_PASSWORD")
client = genai.Client(api_key=API_KEY) if API_KEY else None

if APP_PASSWORD and not st.session_state.get("crm_authenticated", False):
    st.title("🤖 AI Sales CRM")
    st.caption("Enter the password to open this CRM demo.")
    with st.form("crm_login"):
        candidate = st.text_input("Demo password", type="password")
        submitted = st.form_submit_button("Open CRM", use_container_width=True)
    if submitted:
        if hmac.compare_digest(candidate, str(APP_PASSWORD)):
            st.session_state.crm_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


# ==========================================================
# PROJECT IMPORTS
# ==========================================================

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from datastore import database
from main import seed_demo_data, log_action

# ==========================================================
# DATA MODEL
# ==========================================================

class Lead(BaseModel):
    client_name: str
    company: str
    deal_value: str = "0"
    deal_stage: str = "New"
    technical_requirements: str = ""
    priority: str = "Low"
    next_action: str = ""

# ==========================================================
# AI LEAD EXTRACTION ENGINE
# ==========================================================

# ==========================================================
# AI LEAD EXTRACTION ENGINE
# ==========================================================

LEAD_EXTRACTION_PROMPT = """
You are an expert AI Sales CRM assistant.

Your job is to analyze meeting notes and extract structured CRM data.

Return ONLY valid JSON.

Schema:

{
    "client_name": "",
    "company": "",
    "deal_value": "",
    "deal_stage": "",
    "technical_requirements": "",
    "priority": "",
    "next_action": ""
}

Rules:

1. deal_value must contain only digits.
2. If deal value is missing return "0".

3. deal_stage must be one of:
- New
- Qualified
- Proposal
- Negotiation
- Closed

4. priority must be:
- High
- Medium
- Low

Decide priority using:
- Deal value
- Urgency
- Customer interest
- Decision maker involvement

5. next_action should be ONE short recommendation.

Examples:
- Send Proposal
- Schedule Demo
- Follow up after 3 days
- Call client tomorrow

Return ONLY valid JSON.

Meeting Notes:
"""


def clean_json(text: str) -> str:
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1)

    if text.startswith("```"):
        text = text.replace("```", "", 1)

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def extract_lead_info(text: str):

    if not text.strip():
        return None

    try:

        response = client.models.generate_content(
           model="gemini-2.5-flash",
            contents=LEAD_EXTRACTION_PROMPT + "\n\n" + text
        )

        result = clean_json(response.text)

        try:
            data = json.loads(result)

        except json.JSONDecodeError:
            st.error("Gemini returned invalid JSON.")
            return None

        if (
            not data.get("client_name")
            and not data.get("company")
        ):
            return None

        return Lead(
            client_name=data.get("client_name", ""),
            company=data.get("company", ""),
            deal_value=str(data.get("deal_value", "0")),
            deal_stage=data.get("deal_stage", "New"),
            technical_requirements=data.get(
                "technical_requirements",
                ""
            ),
            priority=data.get("priority", "Low"),
            next_action=data.get("next_action", "")
        )

    except Exception as e:
     if "429" in str(e):
        st.error(
            "⚠️ Gemini API quota exceeded. Please check your API key or billing in Google AI Studio."
        )
     else:
        st.error(f"AI Error: {e}")

    return None
# ==========================================================
# SECTION 9 : AI EMAIL ENGINE
# ==========================================================
# ==========================================================
# AI FOLLOW-UP EMAIL PROMPT
# ==========================================================

EMAIL_PROMPT = """
You are an expert B2B sales executive.

Write a professional follow-up email.

The email should:

• Thank the client for the meeting.
• Mention the discussed requirements.
• Mention the proposed solution.
• Mention the deal value if available.
• Mention the agreed next action.
• Sound professional and friendly.
• Be concise.
• Include a subject line.
"""


# ==========================================================
# GENERATE FOLLOW-UP EMAIL
# ==========================================================

def generate_followup_email(lead):

    print("Step 1")

    prompt = f"""
{EMAIL_PROMPT}

Client Name:
{lead.client_name}

Company:
{lead.company}

Technical Requirements:
{lead.technical_requirements}

Deal Value:
{lead.deal_value}

Current Stage:
{lead.deal_stage}

Priority:
{lead.priority}

Next Action:
{lead.next_action}
"""

    print("Step 2")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    print("Step 3")

    return response.text
# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def load_leads() -> pd.DataFrame:
    """
    Load all CRM leads from the CSV database.
    """

    rows = database.CRMLeadsDB.get_all()

    if not rows:
        return pd.DataFrame(columns=[
            "client_name",
            "company",
            "deal_value",
            "deal_stage",
            "technical_requirements",
            "priority",
            "next_action",
        ])

    df = pd.DataFrame(rows)

    expected_columns = [
        "client_name",
        "company",
        "deal_value",
        "deal_stage",
        "technical_requirements",
        "priority",
        "next_action",
    ]

    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""

    return df[expected_columns]


def calculate_total_pipeline(df: pd.DataFrame) -> int:
    """
    Calculate total deal value.
    """

    total = 0

    for value in df["deal_value"]:

        try:
            total += int(value)

        except Exception:
            pass

    return total


def count_high_priority(df: pd.DataFrame) -> int:

    if df.empty:
        return 0

    return (df["priority"] == "High").sum()


def load_activity_log():

    log_path = os.path.join(
        ROOT_DIR,
        "activity_log.txt"
    )

    if not os.path.exists(log_path):
        return "No activity yet."

    with open(
        log_path,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()


def add_new_lead(lead: Lead):

    database.CRMLeadsDB.add(

        lead.client_name,

        lead.company,

        lead.deal_value,

        lead.deal_stage,

        lead.technical_requirements,

        lead.priority,

        lead.next_action,
    )

    log_action(
        f"AI created lead : "
        f"{lead.client_name} | "
        f"{lead.company} | "
        f"{lead.priority}"
    )

# ==========================================================
# CUSTOM CSS
# ==========================================================
st.markdown("""
<style>

/* ===============================
   Main Background
================================ */

.stApp{
    background:#0E1117;
}

/* ===============================
   Content Area
================================ */

.block-container{
    padding-top:2rem;
    max-width:1200px;
}

/* ===============================
   Metric Cards
================================ */

div[data-testid="stMetric"]{

    background:#1C1F26;

    border:1px solid #2F3542;

    border-radius:15px;

    padding:22px;

    box-shadow:0px 4px 12px rgba(0,0,0,0.35);

}

/* Metric Label */

div[data-testid="stMetricLabel"]{

    color:#BFC7D5 !important;

    font-size:15px;

    font-weight:600;

}

/* Metric Value */

div[data-testid="stMetricValue"]{

    color:white !important;

    font-size:34px;

    font-weight:bold;

}

/* Metric Delta */

div[data-testid="stMetricDelta"]{

    color:#00E676 !important;

}

/* ===============================
   Text Area
================================ */

textarea{

    font-size:15px;

}

/* ===============================
   Buttons
================================ */

.stButton>button{

    background:#2962FF;

    color:white;

    border-radius:10px;

    border:none;

    padding:0.6rem 1.3rem;

    font-weight:bold;

}

.stButton>button:hover{

    background:#1E4ED8;

}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("🤖 AI Sales CRM")

st.sidebar.markdown("---")

st.sidebar.subheader("📜 Activity Log")

activity_log = load_activity_log()

st.sidebar.text_area(
    label="",
    value=activity_log,
    height=420
)

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Load Demo Data"):

    seed_demo_data()

    log_action("Loaded demo CRM data")

    st.rerun()

# ==========================================================
# MAIN TITLE
# ==========================================================

st.title("🤖 AI Sales CRM")

st.caption(
    "AI-powered CRM that extracts leads, prioritizes opportunities, and recommends the next sales action."
)

if client is None:
    st.warning(
        "AI features are not configured yet. Add GEMINI_API_KEY to your "
        "Streamlit Cloud app secrets to enable meeting analysis and follow-up emails. "
        "You can still explore the demo dashboard."
    )
# ==========================================================
# LOAD CRM DATA
# ==========================================================

leads_df = load_leads()

# ==========================================================
# DASHBOARD METRICS
# ==========================================================

# ==========================================================
# DASHBOARD METRICS
# ==========================================================

leads_df = load_leads()

total_leads = len(leads_df)

pipeline_value = 0

high_priority = 0

for _, row in leads_df.iterrows():

    try:
        pipeline_value += int(row["deal_value"])
    except:
        pass

    if str(row["priority"]).lower() == "high":
        high_priority += 1

c1, c2, c3 = st.columns(3)

c1.metric(
    "📋 Total Leads",
    total_leads
)

c2.metric(
    "💰 Pipeline Value",
    f"${pipeline_value:,}"
)

c3.metric(
    "🔥 High Priority",
    high_priority
)

st.divider()

# ==========================================================
# MEETING NOTES + AI PANEL
# ==========================================================

# ==========================================================
# MEETING NOTES
# ==========================================================

st.subheader("📝 Meeting Notes")

meeting_notes = st.text_area(
    "Paste meeting notes here",
    height=220,
    placeholder="""
Example:

Met Rahul from ABC Pvt Ltd.

Budget is $50,000.

Needs AI chatbot.

Requested proposal by Friday.
"""
)

analyze = st.button(
    "🤖 Analyze Meeting",
    use_container_width=True,
    disabled=(client is None),
)

if analyze:

    if not meeting_notes.strip():

        st.warning("Please enter meeting notes.")

    else:

        status = st.empty()

        status.info("🤖 Reading meeting notes...")
        time.sleep(0.5)

        status.info("🔍 Detecting client and company...")
        time.sleep(0.5)

        status.info("💰 Estimating deal value...")
        time.sleep(0.5)

        status.info("🧠 Calculating AI priority...")
        time.sleep(0.5)

        status.info("📝 Generating next action...")
        time.sleep(0.5)

        lead = extract_lead_info(meeting_notes)

        status.success("✅ AI Analysis Complete!")
        time.sleep(0.8)
        status.empty()

        if lead is None:

            st.error("Unable to extract CRM information.")

        else:

            add_new_lead(lead)

            # Store latest lead
            st.session_state.latest_lead = lead

            # Generate AI follow-up email
            try:
                with st.spinner("📧 Generating follow-up email..."):
                    st.session_state.email = generate_followup_email(lead)

            except Exception:
                st.session_state.email = ""
                st.error(
                    "🚨 AI service is temporarily unavailable (503).\n\n"
                    "Please wait a few seconds and click **Analyze Meeting** again."
                )

            st.success("✅ Lead added successfully!")

            st.rerun()
# ==========================================================
# SECTION 7 : CRM MANAGEMENT
# ==========================================================

# ==========================================================
# SECTION 7 : AI SALES INTELLIGENCE
# ==========================================================

st.divider()

st.markdown("<br>", unsafe_allow_html=True)
st.divider()
st.subheader("📊 CRM Leads")

if "latest_lead" in st.session_state and st.session_state.latest_lead:

    lead = st.session_state.latest_lead

    score = (
        95 if lead.priority == "High"
        else 75 if lead.priority == "Medium"
        else 55
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🎯 AI Lead Score", f"{score}/100")
        st.metric("🔥 Priority", lead.priority)

    with col2:
        st.metric("💰 Deal Value", f"${lead.deal_value}")
        st.metric("📍 Deal Stage", lead.deal_stage)

    with col3:
        st.metric("📈 Win Probability", "90%")
        st.success(f"🚀 {lead.next_action}")

    st.info(
        f"""
### 🧠 AI Reasoning

• Priority is **{lead.priority}**

• Current stage is **{lead.deal_stage}**

• Estimated revenue is **${lead.deal_value}**

• Recommended next action:

**{lead.next_action}**
"""
    )

else:

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🎯 AI Lead Score", "--")
        st.metric("🔥 Priority", "--")

    with col2:
        st.metric("💰 Deal Value", "--")
        st.metric("📍 Deal Stage", "--")

    with col3:
        st.metric("📈 Win Probability", "--")
        st.info("Waiting for AI analysis...")

    


# ==========================================================
# SEARCH
# ==========================================================

st.divider()

search = st.text_input(
    "🔍 Search Client or Company"
)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()
st.subheader("📊 CRM Leads")

filtered_df = leads_df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["client_name"].astype(str).str.contains(search, case=False, regex=False, na=False)
        |
        filtered_df["company"].astype(str).str.contains(search, case=False, regex=False, na=False)
    ]

if filtered_df.empty:
    st.info("No leads available.")
else:
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=350
    )
# ==========================================================
# SECTION 8 : ANALYTICS & AI SALES COACH
# ==========================================================
# ==========================================================
# SECTION 8 : PIPELINE ANALYTICS & AI SALES COACH
# ==========================================================

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

st.subheader("📈 Pipeline Analytics")

col1, col2 = st.columns(2)

with col1:
    stage_counts = leads_df["deal_stage"].value_counts()
    st.bar_chart(stage_counts)

with col2:
    priority_counts = leads_df["priority"].value_counts()
    st.bar_chart(priority_counts)


st.divider()

st.markdown("<br>", unsafe_allow_html=True)
st.divider()
st.subheader("🤖 AI Sales Coach")

if not leads_df.empty:

    highest = leads_df.assign(
        _numeric_deal_value=pd.to_numeric(leads_df["deal_value"], errors="coerce").fillna(0)
    ).sort_values(by="_numeric_deal_value", ascending=False).iloc[0]

    st.success(f"""
## 🚀 Best Opportunity

👤 **Client:** {highest.client_name}

🏢 **Company:** {highest.company}

💰 **Deal Value:** ${highest.deal_value}

🔥 **Priority:** {highest.priority}

📍 **Stage:** {highest.deal_stage}

📌 **Recommended Action:** {highest.next_action}
""")
    

    
# ==========================================================
# SECTION 10 : AI FOLLOW-UP EMAIL
# ==========================================================

st.divider()

st.markdown("<br>", unsafe_allow_html=True)
st.divider()
st.subheader("📧 AI Follow-up Email")

if "email" in st.session_state:

    edited_email = st.text_area(
        "Generated Email",
        value=st.session_state.email,
        height=350,
    )

    st.session_state.email = edited_email

    st.success("✅ Follow-up email generated successfully.")

    st.download_button(
        "📥 Download Email",
        st.session_state.email,
        file_name="followup_email.txt"
    )

else:

    st.info("Analyze a meeting to generate an AI follow-up email.")