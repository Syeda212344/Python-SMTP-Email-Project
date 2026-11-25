import logging
from unittest.mock import patch
import send_mail

logging.basicConfig(
    filename="logs/test_run.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
class FakeSMTP:
    def __init__(self, *args, **kwargs): pass
    def ehlo(self): pass
    def starttls(self, context=None): pass
    def login(self, user, password): pass
    def send_message(self, message, to_addrs=None): pass
    def quit(self): pass

with patch.dict("os.environ", {
    "SMTP_HOST": "localhost", "SMTP_PORT": "587",
    "SMTP_USER": "demo-user", "SMTP_PASS": "demo-password",
    "FROM": "student@example.edu"
}):
    with patch("smtplib.SMTP", FakeSMTP):
        assert send_mail.send_plain("recipient@example.com", "Test success", "Hello")
    with patch("smtplib.SMTP", side_effect=OSError("Simulated connection problem")):
        assert send_mail.send_plain("failure@example.com", "Test failure", "This should fail") is False
