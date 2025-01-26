import streamlit as st
import pandas as pd
import time
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
import os

# Set your Groq API key directly
GROQ_API_KEY = "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"

# Define the chatbot class
class GroqChatbot:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")

    def get_response(self, user_input):
        # Append the user's input to the conversation history
        st.session_state.conversation_history.append({"role": "user", "content": user_input})

        # Prepare the conversation history for the prompt
        prompt_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.conversation_history[-5:]])  # Use the last 5 exchanges

        # Create a prompt for the chatbot
        prompt = PromptTemplate.from_template(
            f"""
            ### CONVERSATION HISTORY:
            {prompt_text}

            ### INSTRUCTION:
            Just Give answers for questions asked from the csv file and donot answer for unasked questions and donot give any explanations.Donot answer questions that are unrelated to the students data.
            Give answers in a new line by numbers like 1,2,3 and each new number should be in a new line, mentioning their names roll numbers and skills and linkedin links should be in link form not text .After every linkedin link dont continue on same line.
            """
        )
        
        # Retry mechanism for handling rate limits
        retries = 3
        for attempt in range(retries):
            try:
                response = prompt | self.llm
                result = response.invoke(input={})
                bot_response = result.content.strip()

                # Append the bot's response to the conversation history
                st.session_state.conversation_history.append({"role": "Assistant", "content": bot_response})
                return bot_response
            except OutputParserException as e:
                return f"Error: {str(e)}"
            except Exception as e:
                if 'Rate limit reached' in str(e):
                    wait_time = 60  # Wait for 60 seconds before retrying
                    st.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    return f"Error: {str(e)}"
# Function to load CSV
def load_data(uploaded_file):
    return pd.read_csv(uploaded_file)
def main():
# Streamlit UI setup
   
        st.title("Placements Students Profile data Assistant")
        st.write("Ask your doubts of students data.")

        # Initialize session state variables if they do not exist
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'user_input' not in st.session_state:
            st.session_state.user_input = ""
        if 'csv_processed' not in st.session_state:
            st.session_state.csv_processed = False
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR,'resource',  'Student_profiles.csv')
        # PDF file uploader
        uploaded_file = file_path
        
        if uploaded_file is not None and not st.session_state.csv_processed:
            df = load_data(uploaded_file)
            extracted_text = df.to_string()
        
            st.session_state.csv_processed = True

            # After processing the PDF, prompt the chatbot to start asking questions
            chatbot = GroqChatbot()
        
            initial_question = chatbot.get_response(extracted_text)  # Get the first question based on PDF content
            # st.session_state.conversation_history.append({"role": "Interviewer", "content": initial_question})

        # Display conversation history with styled boxes
        if st.session_state.conversation_history:
            for msg in st.session_state.conversation_history:
                if msg['role'] == 'user':
                    st.markdown(
                        f"""
                        <div style='text-align: right; background-color: #414A4C; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                            <strong>You:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div style='text-align: left; background-color: #000000; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                            <strong> Assistant:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True
                    )

        # Input area for user responses with immediate updates to session state
        user_input=st.chat_input("Your Response:")


        if user_input:
                # Initialize the chatbot instance
                chatbot = GroqChatbot()
                # Get response from the chatbot with the latest user input
                bot_response = chatbot.get_response(user_input)
                st.rerun()

        
if __name__ == "__main__":
    main()
