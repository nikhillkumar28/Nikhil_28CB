import google.generativeai as genai
import json
import streamlit as st
from collections import deque
st.set_page_config(layout="wide")

# Configure Gemini API
genai.configure(api_key="AIzaSyA8GGw1OWAeaddIBV08lZvOtH0jcauM9Rs")

# Load custom pet care knowledge
with open("pet_care_data.json", "r") as file:
    pet_knowledge = json.load(file)

# Store last few messages for context tracking
conversation_history = deque(maxlen=10)

SAFE_SMALL_TALK=["Who are you","how are you","hi","hii","hello","hey",
                 "what can you do","your name","about you"

]
# Expanded pet-related keywords
PET_CARE_KEYWORDS = [
    "pet", "dog", "cat", "puppy", "kitten", "vet", "veterinarian", "food", 
    "diet", "nutrition", "treats", "allergies", "walk", "exercise", "training", 
    "obedience", "grooming", "bathing", "brushing", "haircut", "vaccination", 
    "medicine", "health", "illness", "symptoms", "behavior", "toys", "play", 
    "sleep", "adoption", "breed","breeds", "pet care", "kennel","hi","hii","hello",
]

# Initialize session state for user engagement
if "pet_name" not in st.session_state:
    st.session_state.pet_name = ""
if "user_interactions" not in st.session_state:
    st.session_state.user_interactions = 0

# Ask for pet name
# st.session_state.pet_name = st.text_input("What's your pet's name? 🐶🐱")

def is_pet_related(query):
    """Check if the query is related to pet care."""
    query_lower=query.lower()
    if any(keyword in query_lower for keyword in PET_CARE_KEYWORDS):
        return True
    if any (phrase in query_lower for phrase in SAFE_SMALL_TALK):
        return True
    return False

def get_custom_knowledge(query):
    """Match the query to pet care knowledge."""
    query_lower = query.lower()
    for key, info in pet_knowledge.items():
        if key.lower() in query_lower:
            return info[:150] + "..."
    return None


def classify_query(query):
    query_lower = query.lower()

    # Check for pet care relevance
    if any(keyword in query_lower for keyword in PET_CARE_KEYWORDS):
        return "pet_care"

    # Allowable small talk
    if any(phrase in query_lower for phrase in SAFE_SMALL_TALK):
        return "small_talk"

    return "out_of_scope"

def chatbot(query):
    if not query:
        return "Please provide a message to process."

    query_type = classify_query(query)

    if query_type == "pet_care":
        # Check for custom knowledge first
        custom_response = get_custom_knowledge(query)
        if custom_response:
            conversation_history.append(f"User: {query}")
            conversation_history.append(f"Bot: {custom_response}")
            return f"🐾 {custom_response} 🐾"

        # Else use Gemini with context
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            context = "\n".join(conversation_history)
            full_query = f"Previous Conversation:\n{context}\nUser: {query}"
            response = model.generate_content(full_query, generation_config={"temperature": 0.4, "max_output_tokens": 50})

            if response and response.text:
                conversation_history.append(f"User: {query}")
                conversation_history.append(f"ChatBot: {response.text}")
                return f"🐶 {response.text} 🐶"
            else:
                return "I couldn't find an answer. Try rephrasing your question!"
        except Exception as e:
            return f"Oops! Something went wrong: {str(e)}"
            

    elif query_type == "small_talk":
        # Friendly small talk responses
        responses = {
            "how are you": "I'm doing great! Ready to help you and your pet. 🐾",
            "who are you": "I'm your friendly pet care assistant chatbot! 🐶🐱",
            "what can you do": "I can help you schedule appointments, answer pet care queries, and more!",
            "hello": "Hi there! 👋 How can I assist you and your pet today?",
            "hi": "Hey! Hope you and your pet are doing well. 🐕",
        }
        for key in responses:
            if key in query.lower():
                return responses[key]
        return "Hi! I'm here to help with your pet care needs 🐾"

    else:
        return "I'm here to help with pet care and general questions about me 😊. Try asking about your pet or say hi!"


# Add interactive FAQs
# st.sidebar.markdown("## Frequently Asked Questions")
# faqs = {
#     "🐾 How do I book an appointment?": "You can book an appointment by selecting a slot [here](#).",
#     "📅 What are the available grooming slots?": "Available slots are listed [here](#).",
#     "❌ How do I cancel an appointment?": "You can cancel it by visiting [this page](#).",
#     "📌 Where can I check my scheduled events?": "Check your events in the dashboard [here](#)."
# }
# for question, answer in faqs.items():
#     with st.sidebar.expander(question):
#         st.write(answer)

# # Display pet quiz
# st.markdown("### 🐕 Quick Pet Quiz: How often should you groom your pet?")
# quiz_answer = st.radio("Choose an option:", ["Once a year", "Every 4-6 weeks", "Never"])
# if quiz_answer == "Every 4-6 weeks":
#     st.success("✅ Correct! Regular grooming keeps your pet happy and healthy. 🎉")
# else:
#     st.error("❌ Oops! Grooming is important for your pet's hygiene. Try again!")

# # Reward users with virtual badges
# if st.session_state.user_interactions >= 5:
#     st.balloons()
#     st.success("🏅 You've unlocked the **'Pet Care Pro'** badge! Keep learning about pet care!")


# Example usage: Interactive chat loop
# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("Chatbot: Goodbye!")
#         break
#     response = chatbot(user_input)
#     print("Chatbot:", response)
# my pet got infection what should i do
# I'm sorry to hear that your pet is unwell. However, I can't provide specific advice on medical issues. It's best to consult a veterinarian for proper guidance and treatment for your pet's infection. If you have any other questions, feel free to ask!