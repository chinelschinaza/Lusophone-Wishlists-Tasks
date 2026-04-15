# CHINAZA - Task 2 
"""Read URLs from a CSV file and print the HTTP status code for each.
"""

import csv

import requests

CSV_FILE = "Task 2 - Intern.csv"
TIMEOUT = 15


def load_urls(file_path):
    """Load URLs from the 'urls' column of a CSV file."""
    with open(file_path, "r", encoding="utf-8-sig") as file:
        return [row["urls"] for row in csv.DictReader(file)]


def fetch_status(url):
    """Return (url, status) using HEAD, falling back to GET if HEAD is unsupported."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=TIMEOUT)
        if response.status_code in (405, 501):
            response = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
        return url, str(response.status_code)
    except requests.RequestException as exc:
        return url, f"ERR {type(exc).__name__}"


def main():
    urls = load_urls(CSV_FILE)
    for url in urls:
        url, status = fetch_status(url)
        print(f"({status}) {url}")


if __name__ == "__main__":
    main()
