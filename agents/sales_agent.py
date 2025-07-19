import csv
import os
import threading
import time

# Simulated ADK Components

class Session:
    def __init__(self, metadata):
        self.metadata = metadata
        self.slots = {}
        self.message = ""
        self.followup_triggered = False

class State:
    def __init__(self, next_state=None):
        self.next_state = next_state

    def run(self, session: Session):
        raise NotImplementedError

    def end(self, msg):
        print(msg)
        return None

class Agent:
    def __init__(self, id, initial_state, states):
        self.id = id
        self.initial_state = initial_state
        self.states = states

    def handle(self, session: Session):
        current_state_name = self.initial_state
        while current_state_name:
            state = self.states[current_state_name]
            next_prompt = state.run(session)
            if next_prompt is None:
                break

            session.message = ""
            user_input = [""]

            def timed_input():
                try:
                    user_input[0] = input(next_prompt + "\n> ").strip()
                except Exception:
                    user_input[0] = ""

            input_thread = threading.Thread(target=timed_input)
            input_thread.start()
            input_thread.join(timeout=10)  # 10-second timeout

            if input_thread.is_alive():
                print(f"[Follow-up] Hey {session.slots.get('name')}, are you still there?")
                input_thread.join(timeout=5)  # Extra 5 seconds after follow-up

            if not user_input[0]:
                save_no_response_to_csv(session)
                print("No response received. Alright, no problem. Have a great day!")
                break

            session.message = user_input[0]
            current_state_name = state.next_state

# Utility Functions

def prompt(msg):
    return msg

def save_lead_to_csv(session):
    with open("leads.csv", "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            session.slots.get("lead_id", ""),
            session.slots.get("name", ""),
            session.slots.get("age", ""),
            session.slots.get("country", ""),
            session.slots.get("interest", ""),
            "secured"
        ])

def save_no_response_to_csv(session):
    with open("leads.csv", "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            session.slots.get("lead_id", ""),
            session.slots.get("name", ""),
            "", "", "", "no_response"
        ])

# Define States

class Welcome(State):
    def run(self, session):
        session.slots["lead_id"] = session.metadata.get("lead_id", "unknown")
        session.slots["name"] = session.metadata.get("name", "User")
        return prompt(f"Hey {session.slots['name']}, thank you for filling out the form. I'd like to gather some information from you. Is that okay?")

class Consent(State):
    def run(self, session):
        if "yes" in session.message.lower():
            return prompt("What is your age?")
        else:
            save_no_response_to_csv(session)
            return self.end("Alright, no problem. Have a great day!")

class AskAge(State):
    def run(self, session):
        session.slots["age"] = session.message.strip()
        return prompt("Which country are you from?")

class AskCountry(State):
    def run(self, session):
        session.slots["country"] = session.message.strip()
        return prompt("What product or service are you interested in?")

class AskInterest(State):
    def run(self, session):
        session.slots["interest"] = session.message.strip()
        save_lead_to_csv(session)
        return self.end("Thank you! Your information has been saved.")

# Build the Agent

sales_agent = Agent(
    id="sales-agent",
    initial_state="Welcome",
    states={
        "Welcome": Welcome(next_state="Consent"),
        "Consent": Consent(next_state="AskAge"),
        "AskAge": AskAge(next_state="AskCountry"),
        "AskCountry": AskCountry(next_state="AskInterest"),
        "AskInterest": AskInterest()
    }
)
