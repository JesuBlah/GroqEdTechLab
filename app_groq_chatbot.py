import streamlit as st
import requests
import json

# Initialize Eden AI API client
EDEN_AI_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzJhY2I0NmMtNmM0Yi00YjgyLThmN2UtNjdhZWI2ZTQ2NGIyIiwidHlwZSI6ImFwaV90b2tlbiJ9.HBfjVvf8MemR1BXTesrfNXHtFGcC9rbDGxr4unrCZBQ"  # Replace with your actual Eden AI API key
EDEN_AI_URL = "https://api.edenai.run/v2/text/chat"

# Function to call Eden AI chatbot API
def call_eden_ai_chat(messages, temperature=0.7, max_tokens=1024):
    headers = {
        "Authorization": f"Bearer {EDEN_AI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "providers": "openai",  # You can choose other providers like google, mistral, etc.
        "text": messages[-1]["content"],  # Send the latest user message
        "chatbot_global_action": "Act as a helpful learning assistant",
        "previous_history": messages[:-1],  # Include conversation history
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        response = requests.post(EDEN_AI_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["openai"]["generated_text"]  # Adjust based on provider response
    except Exception as e:
        return f"Eden AI API Error: {str(e)}. Please check your API key or try again later."

st.set_page_config(page_title="Personalized Learning Assistant", page_icon="📚")
st.title("📚 Personalized Learning Assistant (Powered by Eden AI)")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add an initial greeting from the assistant
    st.session_state.messages.append({"role": "assistant", "content": "Hello! How can I help you learn today?"})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask me anything about your studies..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # Create a list of messages including previous context for the Eden AI API
        chat_context = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        
        # Call Eden AI API (no streaming support in free tier, so we process the full response)
        full_response = call_eden_ai_chat(chat_context, temperature=0.7, max_tokens=1024)
        
        if "Eden AI API Error" in full_response:
            st.error(full_response)
            message_placeholder.markdown("Sorry, I am unable to process your request right now due to an API error. Please verify your API key and internet connection.")
        else:
            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})