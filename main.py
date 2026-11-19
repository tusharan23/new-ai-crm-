# B2B Sales & Execution CRM
# Hackathon Project

import os
from datetime import datetime
from datastore import database
from knowledge_base import documents


def log_action(action_description: str):
    """Append a timestamped action to activity_log.txt in the project root."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action_description}\n"
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "activity_log.txt")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)


def seed_demo_data():
    """Seed initial dummy data for demo purposes."""
    database.CRMLeadsDB.clear()
    database.ExecutionTasksDB.clear()
    log_action("Cleared existing CRM_Leads and Execution_Tasks data")

    # ADDED the priority and next_action to our dummy data
    leads = [
        ("Alice Johnson", "Acme Corp", "50000", "Qualified", "Need API integration and SSO", "Medium", "Schedule technical call"),
        ("Bob Smith", "Globex Inc", "120000", "Proposal", "Custom reporting and analytics required", "High", "Send pricing proposal"),
        ("Carol Williams", "Initech", "75000", "Negotiation", "Migration from legacy system", "Medium", "Discuss migration timeline"),
    ]

    # UPDATED the loop to unpack 7 variables and send 7 arguments
    for client_name, company, deal_value, deal_stage, technical_requirements, priority, next_action in leads:
        database.CRMLeadsDB.add(client_name, company, deal_value, deal_stage, technical_requirements, priority, next_action)
        log_action(
            f"Added lead: {client_name} at {company} | Deal value: {deal_value} | Stage: {deal_stage}"
        )

    tasks = [
        ("Prepare proposal for Globex Inc", "Alice Johnson", "2024-12-01", "In Progress", "Globex Inc"),
        ("Schedule technical scoping call", "Bob Smith", "2024-11-20", "Pending", "Acme Corp"),
        ("Deliver migration timeline", "Carol Williams", "2024-11-25", "Completed", "Initech"),
    ]

    for task_description, assignee, deadline, status, linked_client in tasks:
        database.ExecutionTasksDB.add(task_description, assignee, deadline, status, linked_client)
        log_action(
            f"Added task: {task_description} | Assignee: {assignee} | Status: {status} | Linked to: {linked_client}"
        )


def main():
    """Main entry point for the CRM application."""
    print("Welcome to B2B Sales & Execution CRM")
    seed_demo_data()
    print("Demo data initialized.")


if __name__ == "__main__":
    main()
