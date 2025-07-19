import sys
import os
import csv

sys.path.append(os.path.dirname(__file__))

from agents.sales_agent import Session, sales_agent 

def simulate():
    if not os.path.exists("leads.csv"):
        with open("leads.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["lead_id", "name", "age", "country", "interest", "status"])

    n = int(input("How many leads to simulate? "))
    for i in range(n):
        lead_id = input(f"\nLead {i+1} ID: ")
        name = input("Lead name: ")
        session = Session(metadata={"lead_id": lead_id, "name": name})
        sales_agent.handle(session)

if __name__ == "__main__":
    simulate()