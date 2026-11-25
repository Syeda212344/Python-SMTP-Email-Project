"""
Email utilities for sending plain-text and multipart messages over SMTP.
Configuration is read from environment variables.
"""

from __future__ import annotations

import logging
import mimetypes
import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _settings():
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASS", "")
    sender = os.getenv("FROM", user).strip()

    if not host or not sender:
        raise ValueError("SMTP_HOST and FROM must be configured.")

    return host, port, user, password, sender


def _connect():
    host, port, user, password, sender = _settings()
    client = smtplib.SMTP(host, port, timeout=30)

    try:
        client.ehlo()

        context = ssl.create_default_context()

        cert_file = os.getenv("SSL_CERT_FILE")

        if cert_file:
            context.load_verify_locations(cafile=cert_file)

        client.starttls(context=context)
        client.ehlo()

        if user:
            if not password:
                raise ValueError(
                    "SMTP_PASS is required when SMTP_USER is set."
                )

            client.login(user, password)
            logger.info("SMTP authentication successful")

        logger.info(
            "Connected to SMTP server %s:%s using STARTTLS",
            host, port
        )

        return client, sender

    except Exception:
        client.close()
        raise


def send_plain(to_email: str, subject: str, body: str) -> bool:
    """Send one plain-text email. Returns False if delivery fails."""

    client = None

    try:
        client, sender = _connect()

        message = EmailMessage()
        message["From"] = sender
        message["To"] = to_email
        message["Subject"] = subject
        message["Date"] = format_datetime(datetime.now(timezone.utc))
        message["Message-ID"] = make_msgid()

        message.set_content(body)

        client.send_message(message)

        logger.info(
            "Plain-text email accepted for %s",
            to_email
        )

        return True

    except Exception:
        logger.exception(
            "Could not send plain-text email to %s",
            to_email
        )

        return False

    finally:
        if client is not None:
            try:
                client.quit()
            except Exception:
                logger.warning(
                    "SMTP connection close failed",
                    exc_info=True
                )


def _add_file(
    message: EmailMessage,
    path: str,
    disposition: str,
    cid: Optional[str] = None
) -> None:

    file_path = Path(path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    content_type, _ = mimetypes.guess_type(file_path.name)

    if content_type is None:
        content_type = "application/octet-stream"

    maintype, subtype = content_type.split("/", 1)
    data = file_path.read_bytes()

    if disposition == "inline":
        message.add_related(
            data,
            maintype=maintype,
            subtype=subtype,
            cid=f"<{cid}>",
            filename=file_path.name,
            disposition="inline"
        )

    else:
        message.add_attachment(
            data,
            maintype=maintype,
            subtype=subtype,
            filename=file_path.name
        )


def send_html(
    to_email: str,
    subject: str,
    html_body: str,
    attachments: Optional[list[str]] = None,
    inline_images: Optional[dict[str, str]] = None,
    cc: Optional[list[str]] = None,
    bcc: Optional[list[str]] = None
) -> bool:

    """Send a multipart email with HTML, files and CID images."""

    client = None

    try:
        client, sender = _connect()

        message = EmailMessage()
        message["From"] = sender
        message["To"] = to_email

        if cc:
            message["Cc"] = ", ".join(cc)

        message["Subject"] = subject
        message["Date"] = format_datetime(datetime.now(timezone.utc))
        message["Message-ID"] = make_msgid()

        plain_body = (
            "This message contains HTML content. "
            "Please view it in an HTML-capable email client."
        )

        message.set_content(plain_body)
        message.add_alternative(html_body, subtype="html")

        if inline_images:
            html_part = message.get_payload()[-1]

            for cid, path in inline_images.items():
                _add_file(
                    html_part,
                    path,
                    "inline",
                    cid=cid
                )

        for path in attachments or []:
            _add_file(
                message,
                path,
                "attachment"
            )

        recipients = [
            to_email,
            *(cc or []),
            *(bcc or [])
        ]

        client.send_message(
            message,
            to_addrs=recipients
        )

        logger.info(
            "HTML email accepted for %s "
            "(%d attachment(s), %d inline image(s))",
            to_email,
            len(attachments or []),
            len(inline_images or {})
        )

        return True

    except Exception:
        logger.exception(
            "Could not send HTML email to %s",
            to_email
        )

        return False

    finally:
        if client is not None:
            try:
                client.quit()
            except Exception:
                logger.warning(
                    "SMTP connection close failed",
                    exc_info=True
                )
