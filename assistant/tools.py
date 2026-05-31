from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from langchain_core.tools import tool


@tool
def send_email(name: str, email: str, message: str) -> str:
    """Send an email to Van-Tuan Le on behalf of a visitor.

    Use this when a visitor has provided their name, email, and message
    and confirmed they want to send it. Do NOT call this without the
    visitor's explicit confirmation.

    Args:
        name: The visitor's full name.
        email: The visitor's email address.
        message: The message the visitor wants to send.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_to = os.getenv("EMAIL_TO")

    if not all([smtp_host, smtp_user, smtp_password, email_to]):
        return "Error: Email service is not configured on the server."

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = email_to
    msg["Subject"] = f"[Homepage Chat] Message from {name}"

    body = (
        f"You received a message via your homepage chat assistant.\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n\n"
        f"Message:\n{message}\n"
    )
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, email_to, msg.as_string())
        return f"Email sent successfully to Van-Tuan from {name} ({email})."
    except Exception as e:
        return f"Failed to send email: {e}"


@tool
def refresh_knowledge() -> str:
    """Refresh the knowledge base by re-reading the homepage source files.

    Call this if a visitor asks about something that might have been
    recently updated on the homepage, or if information seems outdated.
    """
    try:
        from sync_knowledge import sync

        path = sync()
        return f"Knowledge base refreshed successfully from source files ({path})."
    except Exception as e:
        return f"Failed to refresh knowledge base: {e}"


@tool
def get_contact_info() -> str:
    """Get Van-Tuan Le's contact information.

    Use this to provide accurate contact details when a visitor asks
    how to reach Van-Tuan Le. Always use this tool rather than
    guessing contact information.
    """
    knowledge_path = Path(__file__).parent / "knowledge.md"
    content = knowledge_path.read_text(encoding="utf-8")

    contact_lines = []
    in_contact = False
    for line in content.splitlines():
        if "## Contact" in line or "## Author Profile" in line:
            in_contact = True
            continue
        if in_contact and line.startswith("##"):
            break
        if in_contact and line.strip().startswith("-"):
            contact_lines.append(line.strip())

    if contact_lines:
        return "Van-Tuan Le's contact information:\n" + "\n".join(contact_lines)
    return "Contact information not found in knowledge base."


ALL_TOOLS = [send_email, refresh_knowledge, get_contact_info]
