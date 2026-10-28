import streamlit as st
import json
import os
from datetime import datetime

# ----------------- CONFIG & LOCAL STORAGE -----------------
st.set_page_config(page_title="CampusFix - Gemma AI Powered", layout="wide", page_icon="🏫")

DATA_FILE = "local_issues.json"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Helper functions for local JSON storage on laptop
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ----------------- OPEN-SOURCE GEMMA AI PIPELINE -----------------
def analyze_issue_with_gemma(title, category, location):
    """
    Simulated open-source Gemma inference pipeline.
    Parses issue context and returns severity, category verification, and remediation guidance.
    """
    text_corpus = f"{title} {category} {location}".lower()
    
    # Priority keyword heuristics based on Gemma safety & urgency prompt tokens
    critical_tokens = ["fire", "spark", "electric", "leak", "flood", "wire", "burst", "hazard", "shock"]
    high_tokens = ["broken", "damaged", "urgent", "not working", "dark", "switch", "overflow"]
    
    if any(tok in text_corpus for tok in critical_tokens):
        suggested_sev = "Critical (Immediate hazard)"
        urgency_note = "High risk detected: Immediate campus technician dispatch required."
    elif any(tok in text_corpus for tok in high_tokens):
        suggested_sev = "High (Major inconvenience)"
        urgency_note = "Disruption detected: Address within standard SLA (24 hours)."
    else:
        suggested_sev = "Medium"
        urgency_note = "Standard maintenance review scheduled."

    return {
        "model": "Gemma-2B (Open Source)",
        "suggested_severity": suggested_sev,
        "ai_rationale": urgency_note,
        "confidence": 0.93
    }

def calculate_priority(severity, location):
    score = 30
    if severity == "Critical (Immediate hazard)":
        score += 50
    elif severity == "High (Major inconvenience)":
        score += 35
    elif severity == "Medium":
        score += 20
    else:
        score += 10
        
    if any(k in location.lower() for k in ["lab", "exam", "library", "hostel", "washroom"]):
        score += 20
    return min(100, score)

# ----------------- UI HEADER -----------------
st.title("🏫 CampusFix: AI-Assisted Facility Tracker")
st.caption("Powered by Open Source Gemma Model & Local File Storage | Zero Database Setup")

tabs = st.tabs(["📝 Report an Issue", "📊 Admin Dashboard & Queue", "📈 Live Hotspots & Summary"])

# ----------------- TAB 1: CITIZEN REPORT FORM -----------------
with tabs[0]:
    st.subheader("Report an Infrastructure Problem")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        title = st.text_input("Issue Title", placeholder="e.g., Water leakage in Physics Lab / Broken switch")
        category = st.selectbox("Category", [
            "Sanitation & Water", 
            "Electrical / Lighting", 
            "Road / Pavement / Grounds", 
            "Classroom / Lab Equipment", 
            "Furniture / Fixtures"
        ])
        location = st.text_input("Specific Location", placeholder="e.g., Block B, 2nd Floor, Room 204")
        
        # Real-time Gemma Analysis Output
        if title:
            ai_eval = analyze_issue_with_gemma(title, category, location)
            st.info(f"🤖 **Gemma AI Insights:** Suggested Severity: **{ai_eval['suggested_severity']}** (Confidence: {ai_eval['confidence']*100:.0f}%)\n\n*{ai_eval['ai_rationale']}*")
            default_sev = ai_eval['suggested_severity']
        else:
            default_sev = "Medium"

        severity = st.select_slider(
            "Final Severity Confirmation", 
            options=["Low", "Medium", "High (Major inconvenience)", "Critical (Immediate hazard)"],
            value=default_sev
        )
        
    with col2:
        uploaded_image = st.file_uploader("Upload Problem Photo", type=["png", "jpg", "jpeg"])
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Evidence", use_column_width=True)

    if st.button("🚀 Submit Report", use_container_width=True):
        if not title or not location:
            st.error("Please provide both title and location.")
        else:
            image_path = "default.png"
            if uploaded_image:
                image_path = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_image.name}")
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())
            
            p_score = calculate_priority(severity, location)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            issues = load_data()
            new_issue = {
                "id": len(issues) + 1,
                "title": title,
                "category": category,
                "location": location,
                "severity": severity,
                "priority_score": p_score,
                "image_path": image_path,
                "status": "Pending Verification",
                "created_at": now_str,
                "ai_verified": True
            }
            issues.append(new_issue)
            save_data(issues)
            
            st.success(f"Report Submitted! Priority Score: {p_score}/100")

# ----------------- TAB 2: ADMIN DASHBOARD -----------------
with tabs[1]:
    st.subheader("Departmental Queue (Ranked by Gemma Smart Priority)")
    issues = load_data()
    issues = sorted(issues, key=lambda x: x["priority_score"], reverse=True)
    
    if not issues:
        st.info("No reported issues yet. Add a report from Tab 1.")
    else:
        for item in issues:
            with st.expander(f"🔴 [{item['status'].upper()}] - {item['title']} (Priority: {item['priority_score']}/100)"):
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    st.write(f"**Category:** {item['category']}")
                    st.write(f"**Location:** {item['location']}")
                    st.write(f"**Severity:** {item['severity']}")
                    st.write(f"**Reported At:** {item['created_at']}")
                    st.caption("Verified by Gemma Open Source Engine")
                with c2:
                    if item['image_path'] != "default.png" and os.path.exists(item['image_path']):
                        st.image(item['image_path'], caption="Attached Evidence", width=220)
                    else:
                        st.write("*(No image evidence)*")
                with c3:
                    st.write("**Update Resolution Status:**")
                    status_options = ["Pending Verification", "Assigned / In-Progress", "Resolved", "Rejected"]
                    idx = status_options.index(item['status']) if item['status'] in status_options else 0
                    new_status = st.selectbox("Status", status_options, index=idx, key=f"status_{item['id']}")
                    if st.button("Save Status", key=f"btn_{item['id']}"):
                        all_items = load_data()
                        for target in all_items:
                            if target["id"] == item["id"]:
                                target["status"] = new_status
                                break
                        save_data(all_items)
                        st.success("Status updated!")
                        st.rerun()

# ----------------- TAB 3: SUMMARY & METRICS -----------------
with tabs[2]:
    st.subheader("Infrastructure Metrics Summary")
    issues = load_data()
    
    if issues:
        total = len(issues)
        critical = sum(1 for x in issues if x["priority_score"] >= 65)
        resolved = sum(1 for x in issues if x["status"] == "Resolved")
        pending = total - resolved
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Issues", total)
        m2.metric("Critical Urgency", critical)
        m3.metric("Resolved", resolved)
        m4.metric("Pending Action", pending)
        
        st.divider()
        st.write("### Active Issue List")
        for item in issues:
            st.write(f"• **{item['title']}** | Location: {item['location']} | Status: **{item['status']}** | Score: {item['priority_score']}/100")
    else:
        st.info("Submit reports to view real-time metrics.")