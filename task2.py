# CHINAZA - Task 2
"""Read URLs from a CSV file and print the HTTP status code for each."""
import asyncio
import csv

import aiohttp

CSV_FILE = "Task 2 - Intern.csv"
TIMEOUT = aiohttp.ClientTimeout(total=15)


def load_urls(file_path: str) -> list[str]:
    """Load URLs from the 'urls' column of the CSV file."""
    with open(file_path, "r", encoding="utf-8-sig") as file:
        return [row["urls"] for row in csv.DictReader(file)]


async def fetch_status(session: aiohttp.ClientSession, url: str) -> tuple[str, str]:
    """Return (url, status) using HEAD, falling back to GET if HEAD is unsupported."""
    try:
        async with session.head(url, allow_redirects=True) as response:
            if response.status in (405, 501):
                async with session.get(url) as get_response:
                    return url, str(get_response.status)
            return url, str(response.status)
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        return url, f"ERR {type(e).__name__}"


async def main() -> None:
    urls = load_urls(CSV_FILE)
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        results = await asyncio.gather(*(fetch_status(session, url) for url in urls))
    for url, status in results:
        print(f"({status}) {url}")


if __name__ == "__main__":
    asyncio.run(main())
