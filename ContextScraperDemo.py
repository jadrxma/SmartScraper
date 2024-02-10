import streamlit as st
import openai
from bs4 import BeautifulSoup
import requests
import re

# Function to estimate token count
def estimate_tokens(text):
    return len(text.split())

# Function to scrape and clean website content
def scrape_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        cleaned_text = re.sub(r'\s+', ' ', text)
        return cleaned_text
    except Exception as e:
        st.error(f"Error scraping website: {e}")
        return ""

# Initialize session state for storing messages if not already done
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'website_content' not in st.session_state:
    st.session_state['website_content'] = ""

# Sidebar for API key input
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    st.markdown("[Get an OpenAI API Key](https://platform.openai.com/account/api-keys)")
  

# Main app
st.title("💬 Your Personal AI Scraper")

# Input for website URL
website_url = st.text_input("Enter a website URL to scrape for context")

# Button to scrape website
if st.button('Scrape Website'):
    if website_url:
        with st.spinner('Scraping website...'):
            scraped_content = scrape_website(website_url)
            if scraped_content:
                st.session_state['website_content'] = scraped_content  # Store scraped content
                st.text_area("Scraped content (preview)", value=scraped_content[:50000], height=250)
            else:
                st.error("Failed to scrape content. Please check the URL and try again.")
    else:
        st.error("Please enter a website URL.")

# Chat input
user_input = st.text_input("What Would You Like Me To Analyze?")

# Send button for chat
# Chat input and 'Send' button interaction


# Send button for chat
if st.button('Send'):
    if user_input:
        if not openai_api_key:
            st.warning("Please enter your OpenAI API key in the sidebar to continue.")
        else:
            openai.api_key = openai_api_key
            
            # Prepare the context message with a prefix
            context_prefix = "Based on this scrape on a website: "
            full_context = context_prefix + st.session_state.get('website_content', '')
            context_message = {"role": "system", "content": full_context}
            user_message = {"role": "user", "content": user_input}
            messages = [context_message, user_message]
            
            # Estimate tokens for the request
            request_tokens = estimate_tokens(full_context) + estimate_tokens(user_input)
            
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4-0125-preview",  # Adjust as needed
                    messages=messages
                )
                chat_response = response.choices[0].message['content']
                
                # Estimate tokens for the response
                response_tokens = estimate_tokens(chat_response)
                
                # Display token usage information
                total_tokens = request_tokens + response_tokens
                st.write(f"Estimated tokens used: Request: {request_tokens}, Response: {response_tokens}, Total: {total_tokens}")
                
                # Display the response
                st.write(chat_response)
                
                # Optionally, append to session_state for history
                st.session_state['messages'].extend([user_message, {"role": "assistant", "content": chat_response}])
                
            except Exception as e:
                st.error(f"Failed to call OpenAI API: {e}")

# Optionally display the chat history
st.write("Chat History:")
for msg in st.session_state.get('messages', []):
    st.text(f"{msg['role'].capitalize()}: {msg['content']}")
