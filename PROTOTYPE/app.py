import os
import streamlit as st
import joblib
import pandas as pd
import folium
import streamlit.components.v1 as components

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="EventFlow AI",
    page_icon="🚦",
    layout="centered"
)

# =========================
# GLOBAL FAST-FIX CSS
# =========================
# This fixes the cursor globally so you only see the "hand" pointer on dropdowns
st.markdown("""
    <style>
    /* Force 'hand' pointer on the select box and ALL its inner elements */
    div[data-baseweb="select"], div[data-baseweb="select"] * {
        cursor: pointer !important;
    }
    /* Hide the blinking typing line completely */
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE ROUTER
# =========================
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

if 'prediction_inputs' not in st.session_state:
    st.session_state.prediction_inputs = {}

def go_to_form():
    st.session_state.current_page = "form"

def go_to_home():
    st.session_state.current_page = "home"

# =========================
# LOAD MODELS (ABSOLUTE PATH FIX)
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "MODELS"))

model_closure = joblib.load(os.path.join(MODELS_DIR, 'model_closure.pkl'))
model_priority = joblib.load(os.path.join(MODELS_DIR, 'model_priority_v2.pkl'))

le_dict = joblib.load(os.path.join(MODELS_DIR, 'le_dict.pkl'))
le_dict_priority = joblib.load(os.path.join(MODELS_DIR, 'le_dict_priority.pkl'))

impact_scores = joblib.load(os.path.join(MODELS_DIR, 'impact_scores.pkl'))

# =========================
# PAGE 1: LANDING PAGE
# =========================

if st.session_state.current_page == "home":
    
    # Sleek, self-contained home page UI (No external CSS needed)
    st.markdown("""
        <style>
        .landing-container { text-align: center; margin-top: 10vh; margin-bottom: 5vh; }
        .traffic-light { font-size: 5rem; animation: pulse 2s infinite; }
        .main-title { font-size: 3.5rem; font-weight: 800; margin-bottom: 0px; }
        .sub-title { font-size: 1.5rem; color: #888; }
        @keyframes pulse {
            0% { text-shadow: 0 0 10px rgba(255,165,0,0.5); }
            50% { text-shadow: 0 0 40px rgba(255,165,0,1); }
            100% { text-shadow: 0 0 10px rgba(255,165,0,0.5); }
        }
        </style>
        <div class="landing-container">
            <div class="traffic-light">🚦</div>
            <h1 class="main-title">EventFlow AI</h1>
            <p class="sub-title">Event-Driven Traffic Impact Intelligence System</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.success("✅ Models loaded successfully!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.button("🚀 Start System", use_container_width=True, on_click=go_to_form)

# =========================
# PAGE 2: INPUT FORM
# =========================

elif st.session_state.current_page == "form":
    
    st.title("🚦 EventFlow AI")
    st.subheader("Event-Driven Traffic Impact Intelligence System")
    st.markdown("---")

    # DEMO SCENARIOS
    st.markdown("## 🎯 Demo Scenarios")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**HIGH RISK**\n\nEvent: VIP Movement\n\nExpected: 🔴 High Impact")
    with col2:
        st.warning("**MEDIUM RISK**\n\nEvent: Public Event\n\nExpected: 🟠 Medium Impact")
    with col3:
        st.success("**LOW RISK**\n\nEvent: Vehicle Breakdown\n\nExpected: 🟢 Low Impact")

    st.markdown("---")

    # INPUTS
    col1, col2 = st.columns(2)

    with col1:
        event_type = st.selectbox(
            "Event Type", 
            ["unplanned", "planned"],
            index=None,
            placeholder="-- Select --"
        )
        event_cause = st.selectbox(
            "Event Cause",
            ["vehicle_breakdown", "accident", "construction", "pot_holes", "water_logging", 
             "tree_fall", "congestion", "road_conditions", "public_event", "procession", 
             "vip_movement", "protest", "others"],
            index=None,
            placeholder="-- Select --"
        )

    with col2:
        zone = st.selectbox(
            "Zone",
            ["Central Zone 1", "Central Zone 2", "North Zone 1", "North Zone 2", 
             "South Zone 1", "South Zone 2", "East Zone 1", "East Zone 2", 
             "West Zone 1", "West Zone 2", "Unknown"],
            index=None,
            placeholder="-- Select --"
        )
        corridor = st.selectbox(
            "Corridor",
            ["Non-corridor", "Mysore Road", "Bellary Road 1", "Bellary Road 2", 
             "Tumkur Road", "Hosur Road", "ORR North 1", "ORR North 2", 
             "ORR East 1", "ORR East 2", "ORR West 1", "Old Madras Road", 
             "Magadi Road", "Bannerghata Road", "CBD 2", "Hennur Main Road", 
             "West of Chord Road", "Varthur Road", "Old Airport Road", "Unknown"],
            index=None,
            placeholder="-- Select --"
        )

    junction = st.text_input("Junction", value="Unknown")

    st.markdown("---")

    # PREDICT BUTTON
    if st.button("🔍 Predict Impact", use_container_width=True):
        if None in [event_type, event_cause, zone, corridor]:
            st.error("⚠️ Please make a selection for all dropdown menus before predicting.")
        else:
            st.session_state.prediction_inputs = {
                'event_type': event_type,
                'event_cause': event_cause,
                'zone': zone,
                'corridor': corridor,
                'junction': junction
            }
            st.session_state.current_page = "results"
            st.rerun()

# =========================
# PAGE 3: RESULTS
# =========================

elif st.session_state.current_page == "results":
    
    st.title("🚦 EventFlow AI")
    st.subheader("Event-Driven Traffic Impact Intelligence System")
    st.markdown("---")

    inputs = st.session_state.prediction_inputs
    event_type = inputs['event_type']
    event_cause = inputs['event_cause']
    zone = inputs['zone']
    corridor = inputs['corridor']
    junction = inputs['junction']

    # 1. ROAD CLOSURE MODEL
    input_closure = pd.DataFrame([inputs])
    for col in ['event_type', 'event_cause', 'zone', 'corridor']:
        le = le_dict[col]
        input_closure[col] = input_closure[col].apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else 0
        )
    closure_prob = model_closure.predict_proba(input_closure[['event_type', 'event_cause', 'zone', 'corridor']])[0][1]

    # 2. PRIORITY MODEL
    input_priority = pd.DataFrame([inputs])
    for col in ['event_type', 'event_cause', 'zone', 'junction']:
        le = le_dict_priority[col]
        input_priority[col] = input_priority[col].apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else 0
        )
    
    priority_pred = model_priority.predict(input_priority[['event_type', 'event_cause', 'zone', 'junction']])[0]
    priority_label = "HIGH" if priority_pred == 1 else "LOW"
    
    try:
        priority_conf = model_priority.predict_proba(input_priority[['event_type', 'event_cause', 'zone', 'junction']])[0].max()
    except AttributeError:
        priority_conf = 0.85 

    # 3. IMPACT SCORE & RISK
    impact = impact_scores.get(event_cause, 20.0)

    if impact >= 60:
        risk_level = "🔴 Critical"
    elif impact >= 40:
        risk_level = "🟠 High"
    elif impact >= 25:
        risk_level = "🟡 Medium"
    else:
        risk_level = "🟢 Low"

    # --- TOP NAV BUTTON ---
    st.button("← Start New Prediction", on_click=go_to_form)
    
    # --- UI RENDERING ---
    st.success("Prediction Complete")
    st.markdown("## 📊 Prediction Results")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Priority", priority_label)
    with col2:
        st.metric("Priority Confidence", f"{priority_conf * 100:.1f}%")
    with col3:
        st.metric("Closure Prob", f"{closure_prob * 100:.1f}%")
    with col4:
        st.metric("Risk Level", risk_level)

    # WHY THIS PREDICTION
    st.markdown("---")
    st.markdown("## 🧠 Why This Prediction?")
    st.info(f"**Event Cause:** {event_cause}\n\n**Historical Impact Score:** {impact:.1f}/100\n\n**Road Closure Probability:** {closure_prob*100:.1f}%")

    if impact >= 60:
        st.error(f"{event_cause} historically creates severe traffic disruption.")
    elif impact >= 40:
        st.warning(f"{event_cause} frequently impacts traffic flow.")
    else:
        st.success(f"{event_cause} generally causes limited disruption.")

    if closure_prob > 0.5:
        st.warning("High road closure probability detected. Diversion planning recommended.")
    else:
        st.info("Road closure probability is relatively low.")

    # RESOURCE RECOMMENDATIONS
    officers = 12 if impact > 60 else (8 if impact > 40 else (4 if impact > 25 else 2))
    barricades = "Required" if closure_prob > 0.5 else "Not Required"
    diversion = "Suggested" if closure_prob > 0.5 else "Not Required"

    st.markdown("---")
    st.markdown("## 🚔 Recommendations")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Officers Needed", officers)
    with col2:
        st.metric("Barricades", barricades)
    with col3:
        st.metric("Diversion", diversion)

    # ACTIONS
    st.markdown("---")
    st.markdown("## 📌 Suggested Actions")
    actions = []
    if priority_label == "HIGH": actions.append("Deploy traffic personnel immediately")
    if closure_prob > 0.5:
        actions.append("Prepare diversion routes")
        actions.append("Deploy temporary barricades")
    if impact > 40: actions.append("Issue traffic advisory to commuters")
    if len(actions) == 0: actions.append("Continue monitoring situation")
    
    for action in actions:
        st.write("✅", action)

    # RISK ASSESSMENT & STATUS
    st.markdown("---")
    st.markdown("## 🚨 Risk Assessment")

    if impact >= 60:
        st.error(f"HIGH RISK: {event_cause} is likely to create major traffic disruption.")
        st.markdown("## 🚦 Control Center Status")
        st.error("Status: Emergency Response Recommended")
    elif impact >= 40:
        st.warning(f"MEDIUM RISK: Traffic impact expected. Monitoring and traffic personnel recommended.")
        st.markdown("## 🚦 Control Center Status")
        st.warning("Status: Active Monitoring Required")
    else:
        st.success(f"LOW RISK: Limited traffic impact expected.")
        st.markdown("## 🚦 Control Center Status")
        st.success("Status: Normal Operations")

    # MAP VISUALIZATION
    st.markdown("---")
    st.markdown("## 🗺 Incident Location")

    zone_coords = {
        "Central Zone 1": [12.9716, 77.5946], "Central Zone 2": [12.9780, 77.6000],
        "North Zone 1": [13.0827, 77.5877], "North Zone 2": [13.0500, 77.6100],
        "South Zone 1": [12.9081, 77.6476], "South Zone 2": [12.8900, 77.6200],
        "East Zone 1": [12.9900, 77.7000], "East Zone 2": [12.9700, 77.7300],
        "West Zone 1": [12.9700, 77.5000], "West Zone 2": [12.9800, 77.4700],
        "Unknown": [12.9716, 77.5946]
    }

    coords = zone_coords.get(zone, [12.9716, 77.5946])
    marker_color = "red" if impact >= 60 else ("orange" if impact >= 40 else "green")

    m = folium.Map(location=coords, zoom_start=12)
    folium.Marker(
        coords,
        popup=f"<b>Event:</b> {event_cause}<br><b>Zone:</b> {zone}<br><b>Priority:</b> {priority_label}<br><b>Impact:</b> {impact:.1f}",
        icon=folium.Icon(color=marker_color)
    ).add_to(m)

    components.html(m._repr_html_(), height=400)