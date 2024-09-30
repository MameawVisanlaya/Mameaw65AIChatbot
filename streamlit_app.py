import streamlit as st
import google.generativeai as genai
import os
import random

os.environ["GEMINI_API_KEY"] = "your_actual_api_key_here" 
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

class Conversation:
    def __init__(self):
        self.history = []
        self.round = 0

    def add_exchange(self, speaker, message):
        self.history.append((speaker.name, message))
        self.round += 1

    def get_history(self):
        return self.history

    def get_last_exchange(self):
        return self.history[-1] if self.history else None

class Agent:
    def __init__(self, name, personality):
        self.name = name
        self.personality = personality
        self.memory = []
        self.ai = genai.GenerativeModel("gemini-1.5-flash")

    def listen(self, conversation):
        instruction = "You are discussing whether or not to buy a new matte lipstick. Process this conversation and summarize the key points into memory."
        prompt = f"{instruction}. Here is the last exchange in the conversation: {conversation.get_last_exchange()}" 
        try:
            response = self.ai.generate_content(prompt)
            generated_text = response.text
        except Exception as e:
            generated_text = "Sorry, I could not catch that."
        print(f"{self.name} is thinking: {generated_text}")
        self.memory.append(f"This is my piece of thought: {generated_text}")

    def talk(self, conversation, goal):
        if conversation.round == 0:
            prompt = f"Assume you are {self.name} with a {self.personality} personality. Initiate the conversation with the aim of {goal}."
        else:
            instruction = f"Assume you are {self.name} with a {self.personality} personality. You are discussing whether to buy a novel. Engage in conversation naturally, responding to the last message and keeping the goal of {goal} in mind."
            prompt = f"{instruction} Here is the previous conversation: {conversation.get_history()} This is your memory: {self.memory} The last message was: {conversation.get_last_exchange()[1]}" 

        try:
            response = self.ai.generate_content(prompt)
            generated_text = response.text
        except Exception as e:
            generated_text = "Pardon."
        return generated_text

def generate_agents(num_agents):
    names = [
        "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", 
        "Hank", "Ivy", "Jack", "Kelly", "Liam", "Mia", "Noah", 
        "Olivia", "Peter", "Quinn", "Rachel", "Sam", "Tina"
    ]
    personalities = [
        "friendly", "aggressive", "thoughtful", "cautious", "curious", 
        "optimistic", "pessimistic", "humorous", "serious", "analytical"
    ]

    if num_agents > min(len(names), len(personalities)):
        raise ValueError("Number of agents exceeds the unique combination of names and personalities available.")

    random.shuffle(names)
    random.shuffle(personalities)

    return [Agent(name=names[i], personality=personalities[i]) for i in range(num_agents)]

def simulate_conversation(num_agents, goal, num_conversations):
    agents = generate_agents(num_agents)
    conversation = Conversation()

    for _ in range(num_conversations):
        for agent in agents:
            message = agent.talk(conversation, goal)
            print(f"{agent.name}: {message}")
            conversation.add_exchange(agent, message)

        for other_agent in agents:
            if other_agent != agent:
                other_agent.listen(conversation) 
    return conversation

# ส่วน Streamlit UI
st.title("Agent Conversation Simulation lipstick 💄")

gemini_api_key = st.text_input(
    "Gemini API Key: ",
    placeholder="Type your API Key here...",
    type="password",
    key="gemini_api_key",
)
num_agents = st.number_input("Number of agents:", min_value=2, max_value=20, value=3)
num_conversations = st.number_input("Number of conversations per agent:", min_value=1, max_value=10, value=5)
goal = st.text_input("Conversation goal:", value="Decide to buy a matte lipstick", key="conversation_goal")

if st.button("Start Conversation"):
    if gemini_api_key:
        os.environ["GEMINI_API_KEY"] = gemini_api_key
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])

        conversation = simulate_conversation(num_agents, goal, num_conversations)

        st.subheader("Conversation History")
        for speaker, message in conversation.get_history():
            st.write(f"**{speaker}:** {message}")
    else:
        st.warning("Please enter your Gemini API Key.")