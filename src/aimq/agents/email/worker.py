from aimq.clients.resend import ResendError, resend_client
from aimq.clients.supabase import supabase
from aimq.logger import logger

from .agent import EmailAgent


def process_email_response(job_data: dict) -> dict:
    message_id = job_data.get("message_id")
    workspace_id = job_data.get("workspace_id")
    channel_id = job_data.get("channel_id")

    logger.info(f"Processing email response for message {message_id} in channel {channel_id}")

    try:
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

        logger.info(f"Using assistant: {assistant['name']} ({assistant['model']})")

        system_prompt = assistant.get("system_prompt") or (
            f"You are {assistant['name']}, a helpful AI assistant. "
            "Respond professionally and concisely to emails."
        )

        agent = EmailAgent(
            system_prompt=system_prompt,
            assistant_name=assistant["name"],
            model=assistant.get("model", "gpt-4"),
            temperature=0.7,
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

        sender_result = (
            supabase.client.table("members")
            .select("profile:profiles(email)")
            .eq("id", message["from_member_id"])
            .single()
            .execute()
        )
        to_email = sender_result.data["profile"]["email"]

        reply_subject = message.get("email_subject", "")
        if not reply_subject.startswith("Re:"):
            reply_subject = f"Re: {reply_subject}"

        logger.info(f"Sending email from {from_email} to {to_email}")

        import os

        if os.getenv("DRY_RUN") == "true":
            logger.info("DRY_RUN mode: Skipping actual email send")
            email_result = {"id": "dry-run-email-id"}
        else:
            try:
                email_result = resend_client.send_email(
                    from_email=from_email,
                    to=[to_email],
                    subject=reply_subject,
                    text=response_text,
                    reply_to=from_email,
                )
                logger.info(f"Email sent successfully: {email_result}")
            except ResendError as e:
                logger.error(f"Failed to send email: {e}")
                raise

        response_message_result = (
            supabase.client.table("messages")
            .insert(
                {
                    "workspace_id": workspace_id,
                    "channel_id": channel_id,
                    "type": "email",
                    "from_member_id": None,
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

        logger.info(f"Response message saved: {response_message_result.data[0]['id']}")

        supabase.client.table("messages").update(
            {"status": "processed", "processing_stage": "completed"}
        ).eq("id", message_id).execute()

        return {
            "success": True,
            "message_id": message_id,
            "response_message_id": response_message_result.data[0]["id"],
            "email_sent": True,
        }

    except Exception as e:
        logger.error(f"Error processing email response: {e}", exc_info=True)

        supabase.client.table("messages").update(
            {"status": "failed", "processing_stage": f"error: {str(e)}"}
        ).eq("id", message_id).execute()

        raise
