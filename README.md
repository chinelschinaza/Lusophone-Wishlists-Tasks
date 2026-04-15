# Addressing the Lusophone Technological Wishlist Proposals

This repository contains my solutions to two small tasks that involve processing and presenting data using JavaScript and Python.

---

## Task 1 – JavaScript JSON Formatting

### Objective
Create a JavaScript script that manipulates a JSON object and prints the data in a human-readable format.

### My Approach
For this task, I:

- Created a `formatDate()` function to convert the raw date into a clearer format (e.g., **January 12, 2018**).
- Transformed each object in the provided JSON input into a formatted string containing its **title**, **page ID**, and **creation date**.
- Stored these formatted strings in a `results` array.
- Selected the `results` element in the HTML page and inserted the formatted output, separating each entry with a newline so the information is easy to read.

---

## Task 2 – Python URL Status Checker

### Objective
Create a Python script that reads a list of URLs from a CSV file and prints the HTTP status code for each URL.

### My Approach
To implement this, I:

1. Created a `load_urls(file_path)` function to read URLs from the CSV file and return them as a list.
2. Implemented a `fetch_status(session, url)` function that sends an asynchronous GET request and prints:
   - `(STATUS CODE) URL` if the request succeeds  
   - `(ERR) URL — ErrorType` if a connection or request error occurs.
3. Wrote a `main()` function that:
   - Loads all URLs from the CSV file
   - Creates an `aiohttp` session
   - Sends requests to all URLs concurrently and prints their results.

### Why I used async
Instead of using the standard `requests` library, I chose an **asynchronous approach (`aiohttp`)**. I recently learned about parallelism in a course and wanted to apply it here. Using async requests allows multiple URLs to be checked concurrently, which makes the script more efficient than sending requests one at a time.

### Running the script

```bash
python3 task2.py