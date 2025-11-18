"""
Lightweight Email Service

Environment variables:
- SMTP_HOST
- SMTP_PORT (default 587)
- SMTP_USER
- SMTP_PASSWORD
- SMTP_FROM (fallback to SMTP_USER)
- EMAIL_APPROVAL_TO (optional default recipient)

Provides a simple send() API with HTML/text and optional attachments.
"""
from __future__ import annotations

import os
import smtplib
from typing import List, Optional, Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class EmailService:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASSWORD")
        self.sender = os.getenv("SMTP_FROM") or self.user
        self.enabled = bool(self.host and self.user and self.password and self.sender)

    def send(
        self,
        subject: str,
        to_emails: List[str],
        html: Optional[str] = None,
        text: Optional[str] = None,
        attachments: Optional[List[Tuple[str, bytes, str]]] = None,  # (filename, data, content_type)
    ) -> bool:
        if not self.enabled:
            # Log-only fallback
            print(f"[EmailService] Not configured. Would send to {to_emails}: {subject}")
            return False
        if not to_emails:
            return False
        msg = MIMEMultipart("mixed")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = ", ".join(to_emails)

        # Alternative part for text/html
        alt = MIMEMultipart("alternative")
        if text:
            alt.attach(MIMEText(text, "plain"))
        if html:
            alt.attach(MIMEText(html, "html"))
        msg.attach(alt)

        # Attach files
        for (fname, data, ctype) in (attachments or []):
            try:
                maintype, subtype = ctype.split("/", 1)
                if not maintype or not subtype:
                    raise ValueError("invalid content type")
            except Exception:
                maintype, subtype = "application", "octet-stream"
            part = MIMEBase(maintype, subtype)
            part.set_payload(data)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename=\"{fname}\"")
            msg.attach(part)

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.sender, to_emails, msg.as_string())
        return True


_email_service: Optional[EmailService] = None

def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
