import send_mail
from unittest.mock import patch
from pathlib import Path

settings = {
    "SMTP_HOST": "localhost",
    "SMTP_PORT": "587",
    "SMTP_USER": "demo-user",
    "SMTP_PASS": "demo-password",
    "FROM": "student@example.edu"
}

html = """
<html>
<body>
    <h1>CSC 3360 Email Project</h1>
    <p>HTML email with attachment and inline image.</p>
    <img src="cid:campus">
</body>
</html>
"""

with patch.dict("os.environ", settings):
    with patch("smtplib.SMTP") as smtp:
        send_mail.send_html(
            "recipient@example.com",
            "HTML Email Test",
            html,
            attachments=["attachments/project_info.pdf"],
            inline_images={"campus": "inline/campus_mark.png"}
        )

        client = smtp.return_value
        assert client.starttls.called
        assert client.login.called
        assert client.send_message.called

        message = client.send_message.call_args[0][0]
        types = [part.get_content_type()
                 for part in message.walk()]

        assert "text/plain" in types
        assert "text/html" in types
        assert "application/pdf" in types
        assert "image/png" in types
        assert "multipart/alternative" in types
        assert "multipart/mixed" in types
        assert "multipart/related" in types

        print("PASS: Simulated STARTTLS")
        print("PASS: Simulated SMTP authentication")
        print("PASS: Plain-text alternative")
        print("PASS: HTML email")
        print("PASS: PDF attachment")
        print("PASS: Inline PNG image")
        print("PASS: Multipart MIME structure")

        Path("logs/html_test.eml").write_bytes(
            message.as_bytes()
        )

        print("Email saved to logs/html_test.eml")
        print("All MIME assertions passed.")