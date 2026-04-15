# JavaScript's Quirky Date API — A One-Page Guide

## The bug in one sentence

`new Date("2021-09-13").toLocaleDateString("en-US")` prints a different calendar day depending on the viewer's time zone, even though the input has no time component at all.

## Why it happens

When JavaScript parses a date-only ISO string like `"2021-09-13"`, the language spec says it must interpret it as **UTC midnight** (`2021-09-13T00:00:00Z`). Crucially, a JavaScript `Date` object is **not** "a calendar day" — it is a single *instant* in time, stored internally as "milliseconds since the Unix epoch". There is no built-in type that represents *just* a date.

`toLocaleDateString` then takes that instant and formats it **in the caller's local time zone**. So a reviewer in UTC-3 sees:

```
2021-09-13T00:00:00Z   →   2021-09-12T21:00:00 local (UTC-3)
                       →   "September 12, 2021"   ← off by one day
```

You never asked for a time, but `Date` attached one anyway, and the formatter quietly did a time-zone conversion that rolled the calendar day backwards.

## Why a method called *Date*String still depends on the time

Conceptually, if you only care about the date, it feels like `toLocaleDateString` should "just format the date". But internally the `Date` object has no "date" — only that instant. The formatter has to project the instant into *some* time zone to even decide which calendar day it is, and by default it picks the host's local zone. That is why a method with "Date" in its name is silently sensitive to both time and zone.

## The minimal fix

Tell the formatter which zone to project into by adding `timeZone: "UTC"` to the options. Since the original string was parsed as UTC midnight, projecting it back into UTC always lands on the intended calendar day:

```js
new Date("2021-09-13").toLocaleDateString("en-US", {
  year: "numeric",
  month: "long",
  day: "numeric",
  timeZone: "UTC",
});
// → "September 13, 2021", everywhere
```

This is the change I applied in `Task 1 - Intern.html`.

## The real fix: Temporal

Most of this mess comes from the 1995-vintage `Date` object. The [TC39 Temporal proposal](https://tc39.es/proposal-temporal/) adds new types that cleanly separate the concepts `Date` smooshed together:

- `Temporal.PlainDate` — a calendar day with no time and no time zone. Exactly what this task needs.
- `Temporal.PlainDateTime` — a wall-clock date+time with no zone.
- `Temporal.ZonedDateTime` — an instant anchored to a specific time zone.
- `Temporal.Instant` — a point in time (what `Date` really is).

With Temporal, the bug disappears because the type itself refuses to carry a time zone:

```js
Temporal.PlainDate.from("2021-09-13").toLocaleString("en-US", {
  year: "numeric",
  month: "long",
  day: "numeric",
});
// → "September 13, 2021", regardless of where the code runs
```

Temporal is already shipping in some engines behind flags, and polyfills exist for production use. Until it is universally available, the `timeZone: "UTC"` option is the safest minimal fix.
