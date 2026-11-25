# CSC 3360 – Email Python Project

Student: Syeda Kwashfia Nawal  
University: University of North Carolina at Pembroke  
Course: CSC 3360  
Semester: Fall 2026

## Project Overview

This project demonstrates secure email communication using Python, SMTP, and MIME. It includes plain-text emails, HTML emails, PDF attachments, inline images, personalized bulk emails, rate limiting, retry handling, and transaction logging.

## Project Objectives

- Send plain-text emails using SMTP and STARTTLS.
- Configure SMTP credentials through environment variables.
- Construct multipart HTML emails.
- Include attachments and inline images.
- Support CC and BCC recipients.
- Send personalized emails using CSV recipient information.
- Implement rate limiting, retry handling, and error logging.

## Technologies Used

- Python 3
- smtplib
- email
- ssl
- csv
- logging
- aiosmtpd
- unittest.mock
- OpenSSL
- Visual Studio Code

## Project Structure

| File or Folder | Description |
|---|---|
| send_mail.py | Core email sending functions |
| bulk_mail.py | Personalized bulk email processing |
| debug_smtp.py | Local SMTP testing server |
| test_local.py | Simulated success and failure testing |
| test_html.py | HTML and MIME structure testing |
| recipients.csv | List of 10 test recipients |
| .env.example | SMTP configuration placeholders |
| templates/ | HTML and plain-text email templates |
| attachments/ | PDF attachment |
| inline/ | Inline PNG image |
| logs/ | Email transaction and testing logs |
| screenshots/ | Project execution screenshots |

## SMTP Option Used

This project uses a local SMTP debugging server through aiosmtpd. The server runs on localhost using port 8025 and supports STARTTLS and authentication.

All email messages are processed locally for testing purposes. No messages are delivered to external email accounts.

## Installation

Open the project folder in Visual Studio Code and open a terminal.

Install the required Python package:

```
python3 -m pip install aiosmtpd
```

## TLS Certificate Setup

Generate a local testing certificate using the following commands:

```
mkdir -p certs
openssl req -x509 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem -days 30 -nodes -subj "/CN=localhost"
```

The certificate is used for local STARTTLS testing while maintaining certificate verification. Both certificate files must be generated locally before starting the server; they are not included in the submission.

## Running the SMTP Server

In the first terminal, run:

```
python3 debug_smtp.py
```

Keep the server running while performing email tests.

## Environment Configuration

Open a second terminal and configure the following environment variables:

```
export SMTP_HOST=localhost
export SMTP_PORT=8025
export SMTP_USER=demo-user
export SMTP_PASS=demo-password
export FROM=student@example.edu
export RATE_PER_MIN=60
export SSL_CERT_FILE="$PWD/certs/cert.pem"
```

These credentials are intended only for local testing. No real email passwords are used.

## Part A – Plain-Text Email

Run the following command to test plain-text email sending:

```
python3 -c 'import logging; logging.basicConfig(level=logging.INFO); from send_mail import send_plain; print("Email sent:", send_plain("recipient@example.com", "SMTP Test", "CSC 3360 Python Email Project"))'
```

The test demonstrates SMTP authentication, STARTTLS negotiation, and acceptance of a plain-text email by the local SMTP server.

## Part B – HTML and MIME Email

Run the HTML test:

```
python3 test_html.py
```

The test verifies:

- Plain-text alternative
- HTML content
- PDF attachment
- Inline PNG image
- Multipart MIME structure

The generated email is saved as logs/html_test.eml.

On macOS, the generated email can be previewed using:

```
qlmanage -p logs/html_test.eml
```

## Bulk Email Execution

Run the following command while the local SMTP server is active:

```
python3 bulk_mail.py
```

The program reads recipients.csv, personalizes email content, validates email addresses, and sends messages with rate limiting and retry handling.

## Testing Results

The bulk email test was successfully completed on November 25, 2026.

| Test | Result |
|---|---|
| STARTTLS connection | Successful |
| SMTP authentication | Successful |
| HTML email construction | Passed |
| PDF attachment | Included |
| Inline image | Included |
| MIME structure | Passed |
| Recipients processed | 10 |
| Emails accepted by local server | 10 |
| Failed emails during bulk test | 0 |
| Simulated connection failure | Handled |

CC, BCC, and retry functionality are implemented in the source code but were not independently verified through separate live tests.

## Error Handling and Logging

The project records successful email transactions and handled failures.

To run the simulated success and failure tests:

```
python3 test_local.py
```

To review the test logs:

```
cat logs/test_run.log
```

To review the bulk email logs:

```
cat logs/bulk_mail.log
```

## Screenshots

The screenshots folder contains evidence of:

1. Project structure
2. Successful email and handled failure testing
3. Bulk email demonstration logs
4. Attachments and inline image files
5. HTML and MIME testing
6. Generated email preview
7. SMTP server testing
8. Successful bulk email execution

## Assumptions

- Python 3 and OpenSSL are installed.
- The local SMTP server remains active during email execution.
- SMTP credentials are supplied through environment variables.
- All recipients are intended for testing purposes.
- TLS certificates can be generated locally.
- Required templates, attachments, and images remain in their respective directories.

## Conclusion

This project demonstrates secure SMTP communication, STARTTLS authentication, MIME message construction, personalized bulk email processing, and error handling using Python. Local SMTP testing successfully processed 10 email messages without failures.
