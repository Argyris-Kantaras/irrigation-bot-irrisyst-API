import streamlit as st
import requests

netacap_sensors = 0
netacap_sensors_one = 0
gs_one_units = 0

st.set_page_config(page_title="Irrigation Assistant", layout="wide")

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["💬 Chat Assistant", "🛠 System Designer"])

# ---------------Local URLs (DEV)----------------

# API_CHAT_URL = "http://localhost:8000/chat/"
# API_DESIGN_URL = "http://localhost:8000/design_system/"

# ---------------Official URLs----------------
API_CHAT_URL = "https://backend-polished-pine-6029.fly.dev//chat/"
API_DESIGN_URL = "https://backend-polished-pine-6029.fly.dev//design_system/"





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
        system_type = st.selectbox("System Type: ", ["Singlenet", "Radionet", "Multicable"])
        total_valves = st.text_input("Groups of valves(eg. 2 groups of 2 valves and 2 groups of 4 valves): ")

        if system_type == "Radionet":
            netacap_sensors = st.number_input("Netacap sensors ('Max of 8 sensors on Radionet system')", max_value=8, min_value=0)

    with col2:
        controller = st.checkbox("Include GS-MAX Controller?")
        fertikit = st.checkbox("Include Fertikit?")
        ec_ph = st.checkbox("Include EC/PH sensor?")
        weather_station = st.checkbox("Include Weather Station?")
        gs_one = st.checkbox("Include GS-ONE units?")
        if gs_one:
            gs_one_units = st.number_input("How many GS-ONE units?", min_value=1, max_value=20)
            netacap_sensors_one = st.number_input("Netacap sensors (GS-ONE unit can take 1 Netacap)", max_value=20, min_value=0,value=0)

    if system_type == "Multicable":
        controller = True
    if st.button("Generate System Design"):
        payload = {
            "project_name": project_name,
            "system_type": system_type.lower(),
            "total_valves": total_valves,
            "fertikit": fertikit,
            "ec_ph": ec_ph,
            "weather_station": weather_station,
            "controller": controller,
            "gs_one":gs_one,
            "netacap_sensors":netacap_sensors,
            "netacap_sensors_one":netacap_sensors_one,
            "gs_one_units":gs_one_units
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


#upload ---------------
#git add -A
#git commit -m 'commit name'
#git push origin main

#### local run #############
# streamlit run app.py 