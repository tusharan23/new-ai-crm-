import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Runtime files are kept separate from the GitHub repository's source data.
# Cloud hosts may reset this directory at any time; use an external database
# before storing real customer records or relying on permanent persistence.
DATA_DIR = os.getenv("CRM_DATA_DIR", os.path.join(ROOT_DIR, "runtime_data"))
os.makedirs(DATA_DIR, exist_ok=True)
LEADS_FILE = os.path.join(DATA_DIR, "CRM_Leads.csv")
TASKS_FILE = os.path.join(DATA_DIR, "Execution_Tasks.csv")


class CRMLeadsDB:

    columns = [
        "client_name",
        "company",
        "deal_value",
        "deal_stage",
        "technical_requirements",
        "priority",
        "next_action"
    ]

    @classmethod
    def _ensure_file(cls):
        if not os.path.exists(LEADS_FILE):
            pd.DataFrame(columns=cls.columns).to_csv(
                LEADS_FILE,
                index=False
            )

    @classmethod
    def get_all(cls):
        cls._ensure_file()

        df = pd.read_csv(LEADS_FILE)

        return df.to_dict("records")

    @classmethod
    def add(
        cls,
        client_name,
        company,
        deal_value,
        deal_stage,
        technical_requirements,
        priority,
        next_action
    ):
        cls._ensure_file()

        df = pd.read_csv(LEADS_FILE)

        new_row = {
            "client_name": client_name,
            "company": company,
            "deal_value": deal_value,
            "deal_stage": deal_stage,
            "technical_requirements": technical_requirements,
            "priority": priority,
            "next_action": next_action
        }

        df = pd.concat(
            [df, pd.DataFrame([new_row])],
            ignore_index=True
        )

        df.to_csv(
            LEADS_FILE,
            index=False
        )

    @classmethod
    def clear(cls):
        pd.DataFrame(columns=cls.columns).to_csv(
            LEADS_FILE,
            index=False
        )


class ExecutionTasksDB:

    columns = [
        "task_description",
        "assignee",
        "deadline",
        "status",
        "linked_client"
    ]

    @classmethod
    def _ensure_file(cls):
        if not os.path.exists(TASKS_FILE):
            pd.DataFrame(columns=cls.columns).to_csv(
                TASKS_FILE,
                index=False
            )

    @classmethod
    def get_all(cls):
        cls._ensure_file()

        df = pd.read_csv(TASKS_FILE)

        return df.to_dict("records")

    @classmethod
    def add(
        cls,
        task_description,
        assignee,
        deadline,
        status,
        linked_client
    ):

        cls._ensure_file()

        df = pd.read_csv(TASKS_FILE)

        new_row = {
            "task_description": task_description,
            "assignee": assignee,
            "deadline": deadline,
            "status": status,
            "linked_client": linked_client
        }

        df = pd.concat(
            [df, pd.DataFrame([new_row])],
            ignore_index=True
        )

        df.to_csv(
            TASKS_FILE,
            index=False
        )

    @classmethod
    def clear(cls):
        pd.DataFrame(columns=cls.columns).to_csv(
            TASKS_FILE,
            index=False
        )