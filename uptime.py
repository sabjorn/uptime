from enum import Enum, auto
import requests
import argparse
import time
import logging


class APIStatus(Enum):
    UP = auto()
    DOWN = auto()


def _send_email(
    api_key: str, domain: str, email_to: str, subject: str, message: str
) -> None:
    try:
        _ = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": f"API Monitor <mailgun@{domain}>",
                "to": [email_to],
                "subject": subject,
                "text": message,
            },
        )
        logging.info(f"Email sent: {subject}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")


def _check_api(url: str, username: str, password: str) -> APIStatus:
    data = {"username": username, "password": password}
    try:
        response = requests.post(url=url, data=data)
        return APIStatus.UP if response.status_code == 200 else APIStatus.DOWN
    except Exception as e:
        logging.error(f"API check failed: {e}")
        return APIStatus.DOWN


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(
        description="Monitor an API and send alerts on status change."
    )
    parser.add_argument(
        "-u", "--url", required=True, help="The URL of the API to monitor."
    )
    parser.add_argument(
        "-s", "--sleep", type=int, default=60, help="Time in seconds between checks."
    )
    parser.add_argument("--username", required=True, help="Username for API.")
    parser.add_argument("--password", required=True, help="Password for API.")
    parser.add_argument("--mailgun_api_key", required=True, help="Mailgun API key.")
    parser.add_argument("--mailgun_domain", required=True, help="Mailgun domain.")
    parser.add_argument("--email_to", required=True, help="Email to send alerts to.")
    args = parser.parse_args()

    current_status = APIStatus.UP  # Assume API is up initially

    logging.info("API Monitor started. Press Ctrl-C to exit.")
    try:
        while True:
            logging.info("Checking API status...")
            new_status = _check_api(args.url, args.username, args.password)

            if new_status == APIStatus.DOWN and current_status == APIStatus.UP:
                _send_email(
                    args.mailgun_api_key,
                    args.mailgun_domain,
                    args.email_to,
                    "API Status Alert",
                    "The API is down.",
                )
                current_status = APIStatus.DOWN

            elif new_status == APIStatus.UP and current_status == APIStatus.DOWN:
                _send_email(
                    args.mailgun_api_key,
                    args.mailgun_domain,
                    args.email_to,
                    "API Status Recovery",
                    "The API is back up.",
                )
                current_status = APIStatus.UP

            time.sleep(args.sleep)
    except KeyboardInterrupt:
        logging.info("API Monitor shutdown requested. Exiting.")


if __name__ == "__main__":
    main()
