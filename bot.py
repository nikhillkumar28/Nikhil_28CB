import google.generativeai as genai
import json
import streamlit as st
from collections import deque
from difflib import get_close_matches
st.set_page_config (layout="wide")

genai.configure(api_key="AIzaSyA8GGw1OWAeaddIBV08lZvOtH0jcauM9Rs")


with open("pet_care_data.json", "r") as file:
    pet_knowledge = json.load(file)

# Store last few messages for context tracking
conversation_history = deque(maxlen=10)

def is_query_relevant_gemini(query):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        f"Is this query related to pet care: '{query}'? Respond with only Yes or No.",
        generation_config={"temperature": 0.2, "max_output_tokens": 5}
    )
    return "yes" in response.text.lower()

def classify_query(query):
    query_lower = query.lower()

    if is_close_to_keywords(query_lower, PET_CARE_KEYWORDS):
        return "pet_care"

    if any(phrase in query_lower for phrase in SAFE_SMALL_TALK):
        return "small_talk"

    return "out_of_scope"

def is_close_to_keywords(query,keywords,threshold=0.8):
    words=query.lower().split()
    for word in words:
        match=get_close_matches(word,keywords,n=1,cutoff=threshold)
        if match:
            return True
    return False
SAFE_SMALL_TALK=["Who are you","how are you","hi","hii","hello","hey",
                 "what can you do","your name","about you"

]

PET_CARE_KEYWORDS = [
    "pet", "dog", "cat", "puppy", "kitten", "vet", "veterinarian", "food", 
    "diet", "nutrition", "treats", "allergies", "walk", "exercise", "training", 
    "obedience", "grooming", "bathing", "brushing", "haircut", "vaccination", 
    "medicine", "health", "illness", "symptoms", "behavior", "toys", "play", 
    "sleep", "adoption", "breed","breeds", "pet care", "kennel","hi","hii","hello",
]

if "pet_name" not in st.session_state:
    st.session_state.pet_name = ""
if "user_interactions" not in st.session_state:
    st.session_state.user_interactions = 0



def is_pet_related(query):

    query_lower=query.lower()
    if any(keyword in query_lower for keyword in PET_CARE_KEYWORDS):
        return True
    if any (phrase in query_lower for phrase in SAFE_SMALL_TALK):
        return True
    return False

def get_custom_knowledge(query):
    query_lower = query.lower()
    for key, info in pet_knowledge.items():
        if key.lower() in query_lower:
            return info[:150] + "..."
    return None


def classify_query(query):
    query_lower = query.lower()

    if is_close_to_keywords(query_lower, PET_CARE_KEYWORDS):
        return "pet_care"

    if any(phrase in query_lower for phrase in SAFE_SMALL_TALK):
        return "small_talk"

    return "out_of_scope"


def chatbot(query):
    if not query:
        return "Please provide a message to process."
    query_lower=query.lower()
    query_type=classify_query(query)
    if query_type == "out_of_scope":

        if is_query_relevant_gemini(query):
            query_type = "pet_care"
        else:
            return "🙁 Sorry, I specialize in pet care topics only. Try asking something related to pets!"


    if query_type == "pet_care":
        custom_response = get_custom_knowledge(query)
        if custom_response:
            conversation_history.append(f" : {query}")
            conversation_history.append(f" : {custom_response}")
            return f"🐾 {custom_response} 🐾"

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            context = "\n".join(conversation_history)
            full_query = (
    f"You are a helpful pet care assistant. Use clear, brief responses.\n"
    f"Here’s the conversation so far:\n{context}\n"
    f"User: {query}\n"
    f"Assistant:"
)

            response = model.generate_content(full_query, generation_config={"temperature": 0.4, "max_output_tokens": 70})

            if response and response.text:
                conversation_history.append(f" : {query}")
                conversation_history.append(f" : {response.text}")
                return f"🐶 {response.text} 🐶"
            else:
                return "I couldn't find an answer. Try rephrasing your question!"
        except Exception as e:
            return f"Oops! Something went wrong: {str(e)}"
            

    elif query_type == "small_talk":
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



# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("Chatbot: Goodbye!")
#         break
#     response = chatbot(user_input)
#     print("Chatbot:", response)
# my pet got infection what should i do
# I'm sorry to hear that your pet is unwell. However, I can't provide specific advice on medical issues. It's best to consult a veterinarian for proper guidance and treatment for your pet's infection. If you have any other questions, feel free to ask!
