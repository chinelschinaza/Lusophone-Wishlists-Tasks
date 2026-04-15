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

### Reviewer feedback

- **Dates were off by one day in UTC-3.** My reviewer ran the page on a machine in UTC-3 and noticed every article was showing the day *before* its real `creation_date`. The one-line fix was to add `timeZone: "UTC"` to the `toLocaleDateString` options so the formatter always projects the instant into UTC instead of the viewer's local zone:

  ```js
  const options = { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" };
  return new Date(dateStr).toLocaleDateString("en-US", options);
  ```

### What I investigated

- **Why `toLocaleDateString` depends on the viewer's time zone at all.** This bug surprised me — a method with "Date" in its name shouldn't care about time zones, right? It turns out a JavaScript `Date` is really an *instant*, not a calendar day, and `new Date("2021-09-13")` is parsed as **UTC midnight**, which `toLocaleDateString` then projects into the local zone. Newer proposals like [TC39 Temporal](https://tc39.es/proposal-temporal/) add a dedicated `PlainDate` type that fixes this properly. I wrote up a short one-page explainer on the whole thing in [js-date-notes.md](./js-date-notes.md).

---

## Task 2 – Python URL Status Checker

### Objective
Create a Python script that reads a list of URLs from a CSV file and prints the HTTP status code for each URL.

### My Approach
To implement this, I:

1. Created a `load_urls(file_path)` function that reads the CSV file, skips the header row, and returns the URLs as a list.
2. Implemented a `fetch_status(session, url)` function that sends an asynchronous **HEAD** request and returns `(url, status)`, falling back to GET if the server does not accept HEAD.
3. Wrote a `main()` that opens a single `aiohttp.ClientSession`, gathers all requests, and prints each result as `(STATUS) URL` in the same order as the CSV.

### Reviewer feedback I incorporated

- **Use HEAD instead of GET.** Since the task only asks for the status code, Artur pointed out that a HEAD request–the status line and headers without a response body–is enough, which is faster and lighter on both sides than a full GET.

### Design decisions and things I investigated

- **Async (`aiohttp`) over the standard `requests` library.** Checking URLs is I/O-bound, so most of the time is spent waiting on the network. Running the requests concurrently with `asyncio.gather` finishes the whole CSV in a fraction of the time it would take to issue them one at a time.

  ```python
  async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
      results = await asyncio.gather(*(fetch_status(session, url) for url in urls))
  ```

- **HEAD with a GET fallback.** Not every server implements HEAD correctly — some return `405 Method Not Allowed` or `501 Not Implemented`. Instead of reporting those as real statuses, I retry those specific cases with a GET so the reported code reflects the resource itself, not the method.

  ```python
  async with session.head(url, allow_redirects=True) as response:
      if response.status in (405, 501):
          async with session.get(url) as get_response:
              return url, str(get_response.status)
      return url, str(response.status)
  ```

- **A 15-second timeout.** My first runs produced several `ERR` outputs for sites that were simply slow to respond rather than actually broken. Raising the timeout to 15 seconds via `aiohttp.ClientTimeout(total=15)` cleared most of those false errors while still bounding the worst case.

- **Narrow exception handling.** I only catch `aiohttp.ClientError` and `asyncio.TimeoutError` rather than a bare `except Exception`, so genuine bugs still surface instead of being silently labelled as network failures.

- **Following redirects with `allow_redirects=True`.** Many of the URLs in the CSV are old `http://` links that now redirect to `https://`. Following redirects means I report the status of the page the user actually lands on, not the `301`/`302`.

- **Returning results instead of printing inside `fetch_status`.** Because `asyncio.gather` preserves the order of the input coroutines, collecting `(url, status)` tuples and printing them afterwards keeps the output in the same order as the CSV, which is much easier to scan than interleaved prints from concurrent tasks.

- **Reading the CSV with `utf-8-sig` to handle the BOM.** At first I used `next()` to skip `urls` as if it were just the first row, but on inspecting the file I saw that `urls` was actually the column header, so I switched to `csv.DictReader` to select the whole column by name, much like `df["urls"]` in pandas. That crashed with `KeyError: 'urls'` even though the header was clearly there. I found that the CSV was saved as **UTF-8 with a byte-order mark (BOM)**, so the first key was really `"\ufeffurls"`. Opening the file with `encoding="utf-8-sig"` strips that BOM, and `row["urls"]` works as expected.

### Running the script

```bash
pip install -r requirements.txt
python3 task2.py
```
