import streamlit as st
import streamlit.components.v1 as components
import json
import bot
import time
import os
from datetime import datetime

# st.set_page_config(layout="wide")

events_file = "events.json"
users_file = "users.json"

def save_event(event_name, event_time, event_type, user_details):
    try:
        with open(events_file, "r") as file:
            events = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        events = []

    events.append({"title": event_name, "time": event_time, "type": event_type, "details": user_details})

    with open(events_file, "w") as file:
        json.dump(events, file, indent=4)

    return "Appointment successfully booked" if event_type == "Book an appointment" else "Session scheduled"

def load_users():
    if not os.path.exists(users_file):
        return {}
    with open(users_file, "r") as f:
        return json.load(f)

def save_user(username, password):
    users = load_users()
    users[username] = {"password": password}
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)

def validate_user(username, password):
    users = load_users()
    return username in users and users[username]["password"] == password

# Session states
for key in ["messages", "show_form", "selected_option", "user_details", "logged_in", "username"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "messages" else False if key == "logged_in" else None if key == "selected_option" else ""

# Styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Fredoka', sans-serif;
        background: linear-gradient(to right, #e0f7fa, #ede7f6);
    }

    .left-pane {
        background: url('https://images.unsplash.com/photo-1610723057344-e153dd3f6e38') no-repeat center center;
        background-size: cover;
        border-radius: 20px;
        height: 100%;
        padding: 30px;
        color: white;
        margin-top: 100px;
    }

    .nav-links a {
        display: block;
        margin-top: 15px;
        font-size: 18px;
        text-decoration: none;
        color: white;
    }

    .nav-links a:hover {
        text-decoration: underline;
    }

    .chat-container {
        max-width: 80%;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        display: inline-block;
        font-family: Arial, sans-serif;
    }

    .user-message {
        background-color: #DCF8C6;
        text-align: right;
        float: right;
        color: #1A1A1A;
        border: 1px solid #A4D3A2;
    }

    .assistant-message {
        background-color: #EAEAEA;
        text-align: left;
        float: left;
        color: #333333;
        border: 1px solid #C0C0C0;
    }

    .clearfix {
        clear: both;
    }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])
with col1:
    # Set the default active section on first load
    if "active_section" not in st.session_state:
        st.session_state.active_section = "Chat"

    st.markdown("""
        <style>
            .left-pane {
                padding: 20px 15px;
                background-color: #0f0f0f;
                border-right: 1px solid #333;
                border-radius: 12px 0 0 12px;
                height: 50vh;
                max-width: 270px;
                overflow-y: auto;
            }

            .left-pane h2 {
                color: white;
                font-size: 26px;
                margin-bottom: 30px;
            }

            .nav-links a {
                display: block;
                margin-bottom: 20px;
                font-size: 17px;
                color: white;
                text-decoration: none;
                padding-left: 5px;
            }

            .nav-links a:hover {
                text-decoration: underline;
                color: #ccc;
            }
        </style>

        <div class='left-pane'>
            <h2>🐕 Pet Dashboard</h2>
            <div class='nav-links'>
                <a href="#" onclick="fetch('/?section=Schedule').then(() => window.location.reload());">📅 Schedule Appointment</a>
                <a href="#" onclick="fetch('/?section=Tips').then(() => window.location.reload());">📖 Learn Pet Tips</a>
                <a href="#" onclick="fetch('/?section=Chat').then(() => window.location.reload());">💬 Chat with Bot</a>
                <a href="#" onclick="fetch('/?section=Settings').then(() => window.location.reload());">⚙️ Settings</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Simulated JavaScript-triggered section change
    query_params = st.query_params
    if "section" in query_params:
        st.session_state.active_section = query_params["section"][0]



with col2:
    if not st.session_state.logged_in:
        # --- LOGIN / REGISTER PAGE ---
        st.markdown("""
<style>
    .welcome-box {
        background: linear-gradient(135deg, #f7d9ff, #cdb4db);
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        font-size: 24px;
        font-family: 'Fredoka', sans-serif;
        color: #5a189a;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }

    .info-text {
        font-size: 18px;
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
        color: #b39ddb;
        margin-bottom: 20px;
    }
</style>

<div class="welcome-box"><b>
    🐼 𝓦𝓔𝓛𝓒𝓞𝓜𝓔 ! ! 🐼</b><br>
    <b>⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘</b>
</div>

<div class="info-text">
    Please <b>login</b> or <b>sign up</b> to get started with your pet care journey 🐾
</div>
""", unsafe_allow_html=True)

        option = st.radio("Choose an option", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Submit"):
            if option == "Login":
                if validate_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                if username in load_users():
                    st.warning("Username already exists.")
                else:
                    save_user(username, password)
                    st.success("Registration successful! Please login.")
                    time.sleep(1)
                    st.rerun()
        st.stop()

    else:
        # --- MAIN APP CONTENT AFTER LOGIN ---
        active = st.session_state.active_section

        if active == "Schedule":
            st.header("📅 Schedule Appointment")
            # 👉 Paste your schedule form logic here
            st.info("This is where the scheduling form will go.")

        elif active == "Tips":
            st.header("📖 Pet Care Tips")
            st.markdown("""
            - 🐾 Keep vaccinations up to date  
            - 🐶 Regular grooming keeps pets healthy and clean  
            - 🧼 Clean food and water bowls daily  
            - 🏃 Provide daily physical activity  
            - 💧 Fresh water should always be available
            """)

        elif active == "Settings":
            st.header("⚙️ Settings")
            st.info("Settings features coming soon.")

        else:  # Default to Chat
            st.header("💬 Chat with Pet Care Bot")
            # 👉 Paste your chatbot interaction code here
            # Display content based on the selected dashboard section
            if st.session_state.active_section == "schedule":
                st.markdown("### 📅 Schedule an Appointment")
                st.session_state.selected_option = st.radio("Choose an option:", ("Participate in grooming session", "Book an appointment"), index=0)

                with st.form("event_form"):
                    name = st.text_input("Enter your name:")
                    address = st.text_input("Enter your address:")
                    mobile = st.text_input("Enter your mobile number:")
                    slot = st.selectbox("Select preferred slot:", ["Morning", "Afternoon", "Evening"])
                    submitted = st.form_submit_button("Confirm")

                    if submitted:
                        st.session_state.user_details = {"name": name, "address": address, "mobile": mobile, "slot": slot}
                        event_name = "Pet Care Activity"
                        event_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                        response = save_event(event_name, event_time, st.session_state.selected_option, st.session_state.user_details)
                        st.success(response)

            elif st.session_state.active_section == "tips":
                st.markdown("### 📖 Learn Pet Tips")
                st.markdown("""
                - 🐕 Brush your pet regularly to avoid matting.
                - 🐾 Ensure regular vet checkups.
                - 🥗 Feed a balanced diet and provide clean water.
                - 🚶 Give your pet daily exercise and attention.
                """)

            elif st.session_state.active_section == "chat":
                st.markdown("### 💬 Chat with Pet Care Bot")
                for message in st.session_state.messages:
                    align_class = "user-message" if message["role"] == "user" else "assistant-message"
                    st.markdown(f"""
                    <div class='chat-container {align_class}'>{message['content']}</div>
                    <div class='clearfix'></div>
                    """, unsafe_allow_html=True)

                if prompt := st.chat_input("Ask me about pet care or schedule an event..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    response = bot.chatbot(prompt)

        # Simulate typing...
                    message_placeholder = st.empty()
                    for _ in range(3):
                        message_placeholder.markdown("""<div class='chat-container assistant-message'>...</div><div class='clearfix'></div>""", unsafe_allow_html=True)
                        time.sleep(0.5)
                        message_placeholder.markdown("", unsafe_allow_html=True)
                        time.sleep(0.5)

                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.markdown(f"""<div class='chat-container assistant-message'>{response}</div><div class='clearfix'></div>""", unsafe_allow_html=True)

            elif st.session_state.active_section == "settings":
                st.markdown("### ⚙️ Settings")
                st.write("🔐 Feature coming soon: update preferences, theme toggles, etc.")

            





# --- Continue Chatbot and Scheduler UI (unchanged) ---
# Use your same code for chatbot UI and form handling after login.

if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = True

    # Create a placeholder for the temporary welcome message
    welcome_placeholder = st.empty()

    with welcome_placeholder:
        st.markdown(f"""
            <style>
                .welcome-msg {{
                    background: rgba(144, 238, 144, 0.1);
                    padding: 12px 20px;
                    border-radius: 12px;
                    color: #b9fbc0;
                    font-size: 18px;
                    text-align: center;
                    font-family: 'Segoe UI', sans-serif;
                    border: 1px solid #57cc99;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                }}
            </style>
            <div class="welcome-msg">
                👋 Welcome <strong>{st.session_state.username}</strong>! Let's take great care of your pet 🐶🐱
            </div>
        """, unsafe_allow_html=True)
    
    time.sleep(3)  # Show message for 3 seconds
    welcome_placeholder.empty()  # Remove it after 3s

# Title

st.markdown("""
<style>
/* Hide Streamlit default header */
header {visibility: hidden;}

/* Remove Streamlit padding */
.block-container {
    padding-top: 0 !important;
}

/* Sticky header */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: #0e1117;
    color: white;
    padding: 12px 24px;
    z-index: 9999;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    font-family: 'Segoe UI', sans-serif;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
}

/* Center the logo/title */
.navbar .logo {
    grid-column: 2;
    font-size: 34px;
    font-weight: bold;
    color: #80ed99;
    text-align: center;
}

/* Nav links on the right */
.navbar .nav-links {
    grid-column: 3;
    text-align: right;
}
.navbar .nav-links a {
    color: #61dafb;
    margin-left: 20px;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}
.navbar .nav-links a:hover {
    color: #ffffff;
}

/* Theme toggle button */
.toggle-btn {
    background-color: #61dafb;
    color: #0e1117;
    border: none;
    padding: 6px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    margin-left: 20px;
}

/* Push main content down */
.stApp {
    padding-top: 80px !important;
}
</style>

<div class="navbar">
    <div></div> <!-- Left empty column -->
    <div class="logo">🐶 Pet Care Bot</div>
    <div class="nav-links">
        <a href="#dashboard">Dashboard</a>
        <button class="toggle-btn">☀️ Theme</button>
    </div>
</div>
""", unsafe_allow_html=True)


        

# Chat styles
st.markdown("""
<style>
    .chat-container {
        max-width: 80%;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        display: inline-block;
        font-family: Arial, sans-serif;
    }
    .user-message {
        background-color: #DCF8C6;
        text-align: right;
        float: right;
        color: #1A1A1A;
        border: 1px solid #A4D3A2;
    }
    .assistant-message {
        background-color: #EAEAEA;
        text-align: left;
        float: left;
        color: #333333;
        border: 1px solid #C0C0C0;
    }
    .clearfix {
        clear: both;
    }
</style>
""", unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    align_class = "user-message" if message["role"] == "user" else "assistant-message"
    st.markdown(f"""
        <div class='chat-container {align_class}'>
            {message["content"]}
        </div>
        <div class='clearfix'></div>
    """, unsafe_allow_html=True)

# Accept user input
if prompt := st.chat_input("Ask me about pet care or schedule an event..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    if "book an appointment" in prompt.lower() or "schedule an event" in prompt.lower() or"book session" in prompt.lower() or "make appointment" in prompt.lower():
        st.session_state.show_form = True
    else:
        response = bot.chatbot(prompt)

        st.markdown(f"""
            <div class='chat-container user-message'>
                {prompt}
            </div>
            <div class='clearfix'></div>
        """, unsafe_allow_html=True)

        message_placeholder = st.empty()
        for _ in range(3):
            message_placeholder.markdown("""
                <div class='chat-container assistant-message'>...</div>
                <div class='clearfix'></div>
            """, unsafe_allow_html=True)
            time.sleep(0.5)
            message_placeholder.markdown("", unsafe_allow_html=True)
            time.sleep(0.5)

        st.markdown(f"""
            <div class='chat-container assistant-message'>
                {response}
            </div>
            <div class='clearfix'></div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Show scheduling form
if st.session_state.show_form:
    st.markdown("**Would you like to:**")
    st.session_state.selected_option = st.radio("Select an option:", ("Participate in grooming session", "Book an appointment"), index=0)

    with st.form("event_form"):
        name = st.text_input("Enter your name:")
        address = st.text_input("Enter your address:")
        mobile = st.text_input("Enter your mobile number:")
        slot = st.selectbox("Select preferred slot:", ["Morning", "Afternoon", "Evening"])
        submitted = st.form_submit_button("Confirm")

        if submitted:
            st.session_state.user_details = {"name": name, "address": address, "mobile": mobile, "slot": slot}
            event_name, event_time = "Pet Care Activity", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            response = save_event(event_name, event_time, st.session_state.selected_option, st.session_state.user_details)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.success(response)
            st.session_state.show_form = False
st.markdown('</div>', unsafe_allow_html=True)