# Addressing the Lusophone Technological Wishlist Proposals

This repository contains my solutions to two small tasks that involve processing and presenting data using JavaScript and Python.

---

## Task 1 – JavaScript JSON Formatting

### Objective

Create a JavaScript script that manipulates a JSON object and prints the data in a human-readable format.

### My Approach

I wrote a `formatDate()` helper that turns the raw ISO date into something like **January 12, 2018**, then mapped each entry in the JSON to a formatted string of **title**, **page ID**, and **creation date**, and dropped the joined result into the page's `results` element.

### Reviewer feedback

- **Dates were off by one day in UTC-3.** My reviewer ran the page on a machine in UTC-3 and every article showed the day *before* its real `creation_date`. I missed this originally because I only eyeballed the output on my own machine instead of actually testing it — a lesson that directly shaped how I approached Task 2 (see [Practicing code testing](#practicing-code-testing) below). The fix was one extra option on `toLocaleDateString`:

  ```js
  const options = { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" };
  return new Date(dateStr).toLocaleDateString("en-US", options);
  ```

### What I investigated

- **Why `toLocaleDateString` depends on the viewer's time zone at all.** This bug surprised me — a method with "Date" in its name shouldn't care about time zones, right? It turns out a JavaScript `Date` is actually an *instant*, not a calendar day, and `new Date("2021-09-13")` is parsed as **UTC midnight**, which `toLocaleDateString` then projects into the local zone. Newer proposals like [TC39 Temporal](https://tc39.es/proposal-temporal/) add a dedicated `PlainDate` type that fixes this properly. I wrote up a one-page explainer in [js-date-notes.md](./js-date-notes.md).

---

## Task 2 – Python URL Status Checker

### Task objective

Create a Python script that reads a list of URLs from a CSV file and prints the HTTP status code for each URL.

### How I approached it

`load_urls()` reads the URLs out of the CSV, `fetch_status()` sends an async **HEAD** request (falling back to GET if the server doesn't support HEAD), and `main()` opens one `aiohttp.ClientSession`, gathers all the requests, and prints each result as `(STATUS) URL` in the same order as the CSV.

### Reviewer feedback I incorporated

- **Use HEAD instead of GET.** Artur pointed out that since I only need the status code, a HEAD request is enough — the server returns the status and headers without a response body, which is faster and lighter than a full GET.

### Design decisions and things I investigated

- **Async (`aiohttp`) over the standard `requests` library.** Checking URLs is I/O-bound, so most of the time is spent waiting on the network. `asyncio.gather` finishes the whole CSV in a fraction of the time it would take sequentially.

  ```python
  async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
      results = await asyncio.gather(*(fetch_status(session, url) for url in urls))
  ```

- **HEAD with a GET fallback.** A few servers return `405 Method Not Allowed` or `501 Not Implemented` for HEAD. For those specific cases I retry with GET so the reported code reflects the actual resource, not the method.

- **A 15-second timeout.** My first runs produced several `ERR` outputs for sites that were just slow rather than actually broken. Raising the timeout to 15 seconds via `aiohttp.ClientTimeout(total=15)` cleared most of those false errors.

- **Narrow exception handling.** I catch `aiohttp.ClientError` and `asyncio.TimeoutError` rather than a bare `except Exception`, so real bugs still surface.

- **Following redirects with `allow_redirects=True`.** Many CSV URLs are old `http://` links that redirect to `https://`, so this reports the final status rather than the `301`/`302`.

- **Results in CSV order.** `fetch_status` returns `(url, status)` tuples instead of printing, so the output stays in the same order as the CSV — much easier to scan than interleaved prints from concurrent tasks.

- **Reading the CSV with `utf-8-sig` to handle the BOM.** At first I used `next()` to skip `urls` as if it were just the first row, but on inspecting the file I saw that `urls` was actually the column header, so I switched to `csv.DictReader` to select the column by name, much like `df["urls"]` in pandas. That crashed with `KeyError: 'urls'` even though the header was clearly there. I found the CSV was saved as **UTF-8 with a byte-order mark (BOM)**, so the first key was really `"\ufeffurls"`. Opening the file with `encoding="utf-8-sig"` strips the BOM, and `row["urls"]` works.

### Practicing code testing

After the date bug in Task 1 — a bug I would have caught myself if I had actually tested the output in another time zone — I wanted to apply some real code testing to Task 2 as well. I had just started learning about unit testing the week before in my coding classes, so this felt like the right moment to practice on something real.

I first tried writing tests for the async version in [task2.py](./task2.py), but mocking an `aiohttp.ClientSession` and its async context managers turned out to be well beyond what I had learned. Rather than fake my way through something I didn't understand, I wrote a **synchronous companion version** in [task2_sync.py](./task2_sync.py) using the `requests` library. It keeps the same design choices — HEAD with GET fallback, 15-second timeout, `utf-8-sig` CSV reading — but is much easier for a beginner like me to reason about and to mock.

The tests live in [test_task2_sync.py](./test_task2_sync.py). I intentionally kept the suite to a single focused class, `FetchStatusTest`, covering `fetch_status`'s six branches: a successful HEAD, a non-200, the `405` and `501` fallbacks to GET, and the connection-error and timeout paths. Each test uses `unittest.mock.patch` to swap in fake `requests.head`/`requests.get`, so the suite runs offline and deterministically.

```bash
python3 -m unittest test_task2_sync.py -v
```

The async version in [task2.py](./task2.py) is still my main submission — this sync version exists as evidence that I took the testing lesson from Task 1 seriously and practiced what I had just learned, even if I couldn't yet test the async code itself.

### Running the script

```bash
pip install -r requirements.txt
python3 task2.py
```
