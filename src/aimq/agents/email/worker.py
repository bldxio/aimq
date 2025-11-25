import logging
import os
from typing import Any, Dict, Tuple

from aimq.clients.resend import ResendError, resend_client
from aimq.clients.supabase import supabase

from .agent import EmailAgent

logger = logging.getLogger(__name__)


def _get_message_and_assistant(
    message_id: str, channel_id: str
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    message_result = (
        supabase.client.table("messages")
        .select("*, channel:channels(*, primary_assistant:profiles(*))")
        .eq("id", message_id)
        .single()
        .execute()
    )

    if not message_result.data:
        raise ValueError(f"Message {message_id} not found")

    message = message_result.data
    channel = message["channel"]
    assistant = channel.get("primary_assistant")

    if not assistant:
        raise ValueError(f"No primary assistant configured for channel {channel_id}")

    return message, channel, assistant


def _get_assistant_member_id(workspace_id: str, assistant_id: str) -> str:
    assistant_member_result = (
        supabase.client.table("members")
        .select("id")
        .eq("workspace_id", workspace_id)
        .eq("profile_id", assistant_id)
        .single()
        .execute()
    )

    if not assistant_member_result.data:
        raise ValueError(f"Assistant {assistant_id} is not a member of workspace {workspace_id}")

    return assistant_member_result.data["id"]


def _create_email_agent(assistant: Dict[str, Any]) -> EmailAgent:
    system_prompt = assistant.get("system_prompt") or (
        f"You are {assistant['name']}, a helpful AI assistant. "
        "Respond professionally and concisely to emails."
    )

    return EmailAgent(
        system_prompt=system_prompt,
        assistant_name=assistant["name"],
        model=assistant.get("model", "gpt-4"),
        temperature=0.7,
    )


def _get_sender_email(from_member_id: str) -> str:
    sender_result = (
        supabase.client.table("members")
        .select("profile:profiles(email)")
        .eq("id", from_member_id)
        .single()
        .execute()
    )
    return sender_result.data["profile"]["email"]


def _send_email_response(from_email: str, to_email: str, subject: str, text: str) -> Dict[str, Any]:
    if os.getenv("DRY_RUN") == "true":
        logger.info("DRY_RUN mode: Skipping actual email send")
        return {"id": "dry-run-email-id"}

    try:
        email_result = resend_client.send_email(
            from_email=from_email,
            to=[to_email],
            subject=subject,
            text=text,
            reply_to=from_email,
        )
        logger.info(f"Email sent successfully: {email_result}")
        return email_result
    except ResendError as e:
        logger.error(f"Failed to send email: {e}")
        raise


def _save_response_message(
    workspace_id: str,
    channel_id: str,
    assistant_member_id: str,
    message_id: str,
    reply_subject: str,
    to_email: str,
    response_text: str,
    email_result: Dict[str, Any],
) -> str:
    response_message_result = (
        supabase.client.table("messages")
        .insert(
            {
                "workspace_id": workspace_id,
                "channel_id": channel_id,
                "type": "email",
                "from_member_id": assistant_member_id,
                "reply_to_id": message_id,
                "status": "sent",
                "email_subject": reply_subject,
                "email_to": [to_email],
                "content_text": response_text,
                "metadata": {"resend_id": email_result.get("id")},
            }
        )
        .execute()
    )

    response_message_id = response_message_result.data[0]["id"]
    logger.info(f"Response message saved: {response_message_id}")
    return response_message_id


def _update_message_status(message_id: str, status: str, stage: str) -> None:
    supabase.client.table("messages").update({"status": status, "processing_stage": stage}).eq(
        "id", message_id
    ).execute()


def process_email_response(job_data: dict) -> dict:
    message_id = job_data.get("message_id")
    workspace_id = job_data.get("workspace_id")
    channel_id = job_data.get("channel_id")

    logger.info(f"Processing email response for message {message_id} in channel {channel_id}")

    try:
        message, channel, assistant = _get_message_and_assistant(message_id, channel_id)
        assistant_member_id = _get_assistant_member_id(workspace_id, assistant["id"])

        logger.info(f"Using assistant: {assistant['name']} ({assistant['model']})")

        agent = _create_email_agent(assistant)
        system_prompt = assistant.get("system_prompt") or (
            f"You are {assistant['name']}, a helpful AI assistant. "
            "Respond professionally and concisely to emails."
        )

        response_text = agent.generate_response(
            email_subject=message.get("email_subject", ""),
            email_body=message.get("content_text", ""),
            system_prompt=system_prompt,
        )

        logger.info(f"Generated response ({len(response_text)} chars)")

        from_email = message["email_to"][0] if message.get("email_to") else None
        if not from_email:
            raise ValueError("No TO address found in original message")

        to_email = _get_sender_email(message["from_member_id"])

        reply_subject = message.get("email_subject", "")
        if not reply_subject.startswith("Re:"):
            reply_subject = f"Re: {reply_subject}"

        logger.info(f"Sending email from {from_email} to {to_email}")

        email_result = _send_email_response(from_email, to_email, reply_subject, response_text)

        response_message_id = _save_response_message(
            workspace_id,
            channel_id,
            assistant_member_id,
            message_id,
            reply_subject,
            to_email,
            response_text,
            email_result,
        )

        _update_message_status(message_id, "processed", "completed")

        return {
            "success": True,
            "message_id": message_id,
            "response_message_id": response_message_id,
            "email_sent": True,
        }

    except Exception as e:
        logger.error(f"Error processing email response: {e}", exc_info=True)
        _update_message_status(message_id, "failed", f"error: {str(e)}")
        raise
