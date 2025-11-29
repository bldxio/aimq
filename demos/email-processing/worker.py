from aimq.agents.email import process_email_response
from aimq.worker import worker


@worker.task("incoming-messages")
def handle_incoming_message(job_data: dict) -> dict:
    action = job_data.get("action")

    if action == "generate_response":
        return process_email_response(job_data)
    else:
        return {"success": False, "error": f"Unknown action: {action}"}


if __name__ == "__main__":
    worker.run()
