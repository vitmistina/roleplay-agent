import streamlit as st
import json
from typing import Dict, Any
import pandas as pd

class ChatFrontend:
    def __init__(self, chat_manager):
        # Initialize chat manager in session state if it doesn't exist
        if "chat_manager" not in st.session_state:
            st.session_state.chat_manager = chat_manager
        
        # Always use the chat manager from session state
        self.chat_manager = st.session_state.chat_manager
        self.setup_streamlit()

    def setup_streamlit(self):
        st.set_page_config(layout="wide")
        
        # Create main layout
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.title("AI Negotiation Chat")
            self.render_chat_area()
            
        with col2:
            st.subheader("Current State")
            self.render_current_state()
            
        with col3:
            st.subheader("Last Response Analysis")
            self.render_response_analysis()

    def render_chat_area(self):
        # Use the persisted chat manager
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = self.chat_manager.get_conversation_history()
        
        # Display messages from session state
        for i, message in enumerate(st.session_state.chat_history):
            with st.container():
                if isinstance(message, dict):
                    st.markdown(f"**AI**: {message.get('answer', message)}")
                else:
                    is_user = i % 2 == 0
                    st.markdown(
                        f"<div style='padding: 10px; border-radius: 5px; margin: 5px; background-color: {'#f0f0f0' if is_user else '#e3f2fd'}; color: #444444'>"
                        f"<b>{'User' if is_user else 'AI'}</b>: {message}"
                        "</div>",
                        unsafe_allow_html=True
                    )


        def handle_chat_turn():
            if st.session_state.message_input.strip():
                # Use the persisted chat manager
                response = self.chat_manager.take_chat_turn(st.session_state.message_input)
                st.session_state.chat_history = self.chat_manager.get_conversation_history()
                st.session_state.message_input = ""

        # Input area
        prompt = st.text_area("Your message:", key="message_input", height=100, on_change=handle_chat_turn)
        
        # if prompt:
        #     handle_chat_turn()
        
        st.button("Send", on_click=handle_chat_turn)

    def render_current_state(self):
        # Get emotional state directly from chat manager's state
        emotional_state = self.chat_manager.state.get('emotional_state')
        
        if not emotional_state:
            st.write("No emotional state available yet")
            return

        # Display emotional state with color-coded bars
        st.markdown("**Emotional State:**")
        for metric, value in emotional_state.items():
            # Convert -1 to 1 scale to 0 to 1 for color interpolation
            normalized_value = (value + 1) / 2
            color = f'rgb({int(255 * (1-normalized_value))}, {int(255 * normalized_value)}, 0)'
            st.markdown(
                f"""
                <div style="margin-bottom: 10px;">
                    <div style="margin-bottom: 5px;">{metric.replace('_', ' ').title()}: {value:.2f}</div>
                    <div style="width: 100%; background-color: #f0f0f0; height: 20px;">
                        <div style="width: {(value + 1) * 50}%; background-color: {color}; height: 20px;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    def render_response_analysis(self):
        # Get last response if exists
        history = self.chat_manager.get_conversation_history()
        if not history or len(history) < 2:
            st.write("No responses yet")
            return

        last_response = history[-1]
        if isinstance(last_response, str):
            try:
                last_response = json.loads(last_response)
            except json.JSONDecodeError:
                st.write("Last response is not in JSON format")
                return

        # Display internal analysis
        if isinstance(last_response, dict):
            for field in ['internal_dialogue', 'strategy_assessment', 'emotional_processing']:
                if field in last_response:
                    st.markdown(f"**{field.replace('_', ' ').title()}:**")
                    st.write(last_response[field])
