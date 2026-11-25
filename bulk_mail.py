"""Send personalized HTML messages to contacts listed in a CSV file."""
from __future__ import annotations

import csv
import logging
import os
import re
import time
from pathlib import Path

from send_mail import send_html

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "bulk_mail.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)
logger = logging.getLogger(__name__)


def load_template(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def send_bulk(csv_path: Path, template_path: Path) -> tuple[int, int]:
    rate = max(1, int(os.getenv("RATE_PER_MIN", "6")))
    delay = 60.0 / rate
    template = load_template(template_path)
    sent = failed = 0

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"email", "first_name"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV must include email and first_name columns.")

        for row in reader:
            email = row["email"].strip()
            first_name = row["first_name"].strip()
            if not email or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                logger.error("Skipping invalid email address: %r", email)
                failed += 1
                continue

            html = template.replace("{{ first_name }}", first_name)
            success = False
            for attempt in range(1, 4):
                success = send_html(
                    to_email=email,
                    subject="A quick update for you",
                    html_body=html,
                    attachments=[str(ROOT / "attachments" / "project_info.pdf")],
                    inline_images={"campus_mark": str(ROOT / "inline" / "campus_mark.png")},
                )
                if success:
                    break
                logger.warning("Attempt %d failed for %s", attempt, email)
                if attempt < 3:
                    time.sleep(min(2 ** (attempt - 1), 8))

            if success:
                sent += 1
            else:
                failed += 1
            time.sleep(delay)

    logger.info("Bulk run finished: %d sent, %d failed", sent, failed)
    return sent, failed


if __name__ == "__main__":
    send_bulk(ROOT / "recipients.csv", ROOT / "templates" / "email_template.html")
