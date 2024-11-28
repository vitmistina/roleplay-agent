import os
from anthropic import Anthropic


import json

from dotenv import load_dotenv


class ChatStateManager:
    def __init__(self, scenario_json: str):
        load_dotenv()  # Load environment variables from .env file
        ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
        self.json_file = scenario_json
        self.state = self.load_scenario(scenario_json)
        self.system_prompt = self.create_system_prompt()
        self.conversation_history = []
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

    def load_scenario(self, json_file: str):
        with open(self.json_file, 'r') as f:
            return json.load(f)

    def update_state(self, new_data):
        # Update the state with new data
        pass

    def create_system_prompt(self):
        # Load the template
        with open('system_prompt_template.txt', 'r') as f:
            template = f.read()

        char_profile = self.state['character_profile']

        format_dict = {
            'name': char_profile['name'],
            'role': char_profile['role'],
            'gender': char_profile['gender'],
            'goal': self.state['goal'],
            'expertise_domain': char_profile['expertise']['domain'],
            'expertise_yearsExperience': char_profile['expertise']['years_experience'],
            'expertise_hierarchyLevel': char_profile['expertise']['hierarchy_level'],
            'personality': char_profile['personality'],
            'negotiation_style': char_profile['negotiation_style'],
            'counterpart': self.state['counterpart']
        }

        try:
        # Fill the template with explicit error handling
            system_prompt = template.format_map(format_dict)
            return system_prompt
        except KeyError as e:
            print(f"Template key error: {e}")
            print("Template expects:", template)
            raise

    def create_chat_turn(self, message: str) -> str:
        # Load the template
        with open('chat_turn_template.txt', 'r') as f:
            template = f.read()

        # Create a copy of the state and add the message
        current_state = self.state.copy()
        current_state['message'] = message

        try:
            # Fill the template with explicit error handling
            chat_turn = template.format_map(current_state)
            return chat_turn
        except KeyError as e:
            print(f"Template key error: {e}")
            print("Template expects:", template)
            raise

    # method to take a chat turn. Based on the system prompt and template, this can be an example of the response:
    # {
    # "internal_dialogue": "This guardian is trying to emotionally manipulate me with her mother's health situation. They always try to find excuses. I've been managing condominiums for 12 years, and I've seen this pattern before. However, I need to maintain professional composure while being firm.",

    # "strategy_assessment": "She's attempting to create a personal arrangement, which is completely unacceptable and against association policies. I need to redirect this conversation back to official channels and reinforce the collective decision-making process. Using my authority position to emphasize the rules.",

    # "emotional_processing": "Feeling irritated by the attempt to circumvent standard procedures. The suggestion of personal financing arrangements is particularly frustrating. Need to control my natural tendency towards confrontation while maintaining dominance.",

    # "emotional_state": {
    #     "valence": -0.8,
    #     "arousal": 0.5,
    #     "dominance": 0.7,
    #     "stress_level": 0.4,
    #     "trust_level": -0.4,
    #     "frustration_level": 0.8,
    #     "empathy_level": 0.5
    # },

    # "answer": "Ms. Mistinova, while I understand your concerns about your mother's situation, I must be very clear here. Personal financing arrangements between owners are strictly against our association's policies. As chairperson, I cannot and will not engage in such informal agreements. The renovation project requires all owners to contribute their share in cash - this is non-negotiable. The association has voted on this matter, and it's my responsibility to ensure fair and equal treatment for all owners. I can assure you everything will be okay if we follow the proper procedures. Perhaps you could explore other options like family assistance or personal savings? The deadline for cash payments remains firm."
    # }

    def take_chat_turn(self, user_message: str) -> str:
        # Create the formatted chat turn from the template
        formatted_message = self.create_chat_turn(user_message)

        # Create the next message including conversation history
        messages = [
            {"role": "user", "content": msg} if i % 2 == 0 else {"role": "assistant", "content": msg['answer']}
            for i, msg in enumerate(self.conversation_history)
        ]
        messages.append({"role": "user", "content": formatted_message})

        # Call Anthropic API
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=self.system_prompt,
            messages=messages,
            temperature=0.7
        )

        try:
            assistant_response = json.loads(response.content[0].text)
        except json.JSONDecodeError as e:
            print(f"Failed to parse response as JSON: {e}")
            print("Raw response:", response.content[0].text)
            raise

        self.state['emotional_state'] = assistant_response['emotional_state']

        # Update conversation history with the raw message and response
        self.conversation_history.append(user_message)
        self.conversation_history.append(assistant_response)

        return assistant_response

    def get_conversation_history(self) -> list:
        return self.conversation_history

    def clear_conversation(self):
        self.conversation_history = []