#!/usr/bin/env python
"""Test the email agent locally."""

from aimq.agents.email import EmailAgent

system_prompt = """You are Mindi, a helpful AI assistant for Acme Corporation.
You are professional, concise, and friendly.
Always sign your emails with "Best regards, Mindi"."""

agent = EmailAgent(
    system_prompt=system_prompt,
    assistant_name="Mindi",
    model="gpt-4",
    temperature=0.7,
)

email_subject = "Need Help with Project"
email_body = """Hi there,

I'm having trouble understanding the latest project requirements.
Can you help clarify what's expected for the Q1 deliverables?

Thanks!
Jane"""

print("Generating response...")
print("=" * 60)

response = agent.generate_response(
    email_subject=email_subject,
    email_body=email_body,
    system_prompt=system_prompt,
)

print(f"Subject: Re: {email_subject}")
print()
print(response)
print("=" * 60)
