import ssl
import time
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword
from aiosmtpd.handlers import Debugging


def authenticate(server, session, envelope, mechanism, auth_data):
    valid = (
        isinstance(auth_data, LoginPassword)
        and auth_data.login == b"demo-user"
        and auth_data.password == b"demo-password"
    )

    if valid:
        print("SMTP authentication successful", flush=True)
        return AuthResult(success=True)

    return AuthResult(success=False, handled=False)


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(
    "certs/cert.pem",
    "certs/key.pem"
)

controller = Controller(
    Debugging(),
    hostname="127.0.0.1",
    port=8025,
    tls_context=context,
    require_starttls=True,
    auth_required=True,
    authenticator=authenticate
)

controller.start()

print("Local SMTP server running on port 8025")
print("STARTTLS enabled")
print("Authentication required")
print("Waiting for emails...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    controller.stop()