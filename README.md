OTT API Test Automation Framework

A production-style API test automation framework built with Python and PyTest, testing The Movie Database (TMDB) API — chosen to reflect real-world OTT/streaming catalog test scenarios (search, metadata validation, pagination, error handling).

Built by an OTT QA engineer (JioHotstar, JioCinema, Lionsgate Play) transitioning domain expertise into SDET-level automation.

Highlights


Layered architecture — a reusable API client with retry/backoff logic; tests never call requests directly
JSON schema contract validation — catches breaking API changes that field-by-field assertions miss
Data-driven tests — parametrized scenarios expand one test into many cases
Dedicated negative-test suite — invalid IDs, bad auth, malformed input; verifying the API fails safely
CI/CD — GitHub Actions runs smoke tests on every PR, full regression nightly, HTML reports as artifacts
No secrets in code — API keys load from environment variables; the repo is safe to be public


Architecture

ott-api-test-framework/
├── src/
│   ├── api_client.py       # Reusable HTTP client: retries, timeouts, auth injection, logging
│   ├── endpoints.py        # Centralized endpoint definitions
│   └── config_loader.py    # Merges config.yaml with .env secrets
├── tests/
│   ├── conftest.py         # Shared pytest fixtures (session-scoped client)
│   ├── test_movies.py      # Happy path + schema contract + pagination checks
│   ├── test_search.py      # Parametrized, data-driven search scenarios
│   └── test_negative.py    # Error-contract tests (404s, 401s, malformed input)
├── utils/
│   ├── logger.py           # Centralized logging
│   └── schema_validator.py # JSON schema validation helper
├── schemas/movie_schema.json   # The response contract for a movie object
├── config/config.yaml          # Base URL, timeouts, retry settings
├── .github/workflows/ci.yml    # CI pipeline
├── pytest.ini
├── requirements.txt
└── .env.example

Setup

bashgit clone https://github.com/ranjith-rath/ott-api-test-framework.git
cd ott-api-test-framework
pip install -r requirements.txt
cp .env.example .env   # add your free TMDB API key: https://www.themoviedb.org/settings/api

Running tests

bashpytest                                              # full suite
pytest -m smoke                                     # critical-path only
pytest -m negative                                  # error-handling suite
pytest --html=reports/report.html --self-contained-html   # with HTML report

Key design decisions

Why an API client class instead of raw requests calls?
Retries (exponential backoff on 429/5xx — never on 4xx), timeouts, auth injection, and request/response logging live in ONE place. If the auth mechanism changes, one file changes — not every test.

Why JSON schema validation over field asserts?
Field asserts only check what you thought to check. The schema validates the entire contract — types, required fields, value ranges — catching breaking changes (a renamed field, an int becoming a string) in one line of test code.

Why a dedicated negative-test suite?
Coming from OTT entitlement testing: an API that errors wrongly is more dangerous than a broken happy path. These tests pin down the error contract — a nonexistent resource returns 404 (not 200 with junk, not a 500), invalid auth returns 401.

Why are some negative asserts loose (e.g., status in (400, 404))?
Deliberate strictness calibration: for a third-party API, the exact rejection code for garbage input is their choice — the assertable contract is "clean rejection, no crash." For an API my own team owned, I'd pin exact codes.

A real bug story from this repo

On first run, three parametrized tests failed together — the year-filter search tests. All-cases-failing pointed to a systematic assumption, not flaky data. Root cause: the tests used TMDB's year parameter assuming strict filtering by primary release year, but year is fuzzy — it matches any associated release year (regional re-releases, DVD dates). The API was correct; the test encoded a wrong contract assumption. Fix: switch to primary_release_year, TMDB's strict parameter.

Lesson encoded in this suite: a failing test means either a bug or a wrong assumption — root-causing which one is the actual job.

Tech stack

Python 3.14 · pytest · requests · jsonschema · pytest-html · PyYAML · python-dotenv · GitHub Actions

Roadmap

 Response-time assertions (latency thresholds per endpoint)
 Recorded-response mode for deterministic offline runs
 POST/PUT flows with fixture-based teardown
