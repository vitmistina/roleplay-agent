from dotenv import load_dotenv
import streamlit as st
from ChatStateManager import ChatStateManager
from ChatFrontend import ChatFrontend

def main():
    try:
        # Initialize the ChatStateManager with the scenario file
        chat_manager = ChatStateManager('backlog_position.json')
        
        # Initialize and run the frontend
        frontend = ChatFrontend(chat_manager)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()



