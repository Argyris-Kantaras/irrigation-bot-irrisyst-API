import streamlit as st
import requests

st.set_page_config(page_title="Irrigation Assistant", layout="wide")

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["💬 Chat Assistant", "🛠 System Designer"])

# API_CHAT_URL = "http://localhost:8000/chat/"
# API_DESIGN_URL = "http://localhost:8000/design_system/"
# https://irrigation-bot-irrisyst-api.onrender.com
API_CHAT_URL = "https://irrigation-bot-irrisyst-api.onrender.com/chat/"
API_DESIGN_URL = "https://irrigation-bot-irrisyst-api.onrender.com/design_system/"


# ---------------- Chat Page ----------------
if page == "💬 Chat Assistant":
    st.title("💬 Irrigation Chat Assistant")
    st.write("Ask anything about irrigation, systems, valves, or design.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_message = st.text_input("Type your question:")

    if st.button("Send"):
        if user_message.strip():
            # Add user message to chat history
            st.session_state.chat_history.append(("user", user_message))

            # Send to FastAPI
            response = requests.post(API_CHAT_URL, data={"message": user_message})

            if response.status_code == 200:
                bot_reply = response.json().get("reply", "")
                st.session_state.chat_history.append(("bot", bot_reply))
            else:
                st.session_state.chat_history.append(("bot", "Error contacting server."))

    # Display chat history
    for sender, msg in st.session_state.chat_history:
        if sender == "user":
            st.markdown(f"""
            <div style='text-align: right; color: black; background-color: #DCF8C6; padding: 10px; border-radius: 10px; margin: 5px;'>
                <b>You:</b> {msg}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='text-align: left; color: black; background-color: #F1F0F0; padding: 10px; border-radius: 10px; margin: 5px;'>
                <b>Assistant:</b> {msg}
            </div>
            """, unsafe_allow_html=True)

# ---------------- System Designer Page ----------------
elif page == "🛠 System Designer":
    st.title("🛠 Irrigation System Designer")
    st.write("Enter your project details to generate a complete system design Excel file.")

    col1, col2 = st.columns(2)

    with col1:
        project_name = st.text_input("Project Name: ")
        system_type = st.text_input("System Type: ")
        total_valves = st.text_input("Groups of valves(eg. 2 groups of 2 valves and 2 groups of 4 valves): ")

    with col2:
        fertikit = st.checkbox("Include Fertikit?")
        ec_ph = st.checkbox("Include EC/PH sensor?")
        weather_station = st.checkbox("Include Weather Station?")

    if st.button("Generate System Design"):
        payload = {
            "project_name": project_name,
            "system_type": system_type,
            "total_valves": total_valves,
            "fertikit": fertikit,
            "ec_ph": ec_ph,
            "weather_station": weather_station
        }
        response = requests.post(API_DESIGN_URL, data=payload)

        if response.status_code == 200:
            st.success("System design generated successfully!")

            st.download_button(
                label="📥 Download Excel File",
                data=response.content,
                file_name=f"{project_name}_design.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Error generating Excel file.")
            try:
                st.write(response.json())
            except:
                st.write("Unknown error")
