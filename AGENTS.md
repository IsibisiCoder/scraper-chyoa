# Project Overview & Goals
- **Purpose:** A CLI tool written in Python that retrieves the HTML content of a specified URL from the chyoa.com website and saves it locally as a file. The page contains additional links to other sections. These web pages are also retrieved and saved as files.
- **Target Audience:** Users who would like to read and archive the stories from the chypoa website offline.
- **Focus:** Reliable login using sessions, reliability, clean error handling (timeouts, HTTP errors), and safe handling of filenames. Recursion should be avoided by using a queue.

# Tech Stack & Libraries
- **Language:** Python 3.17+
- **HTTP Client:** `requests` (for synchronous requests)
- **HTML Parsing:** `beautifulsoup4` (for cleaning or extracting plain text)
- **CLI:** Standard library `argparse`
- **Tests:** `pytest`

# Language
- The programming language is English. This applies to variables, methods, comments, and the README.

# Target Website chyoa.com
- The website uses PHP 8.5, Laravel 13, and Linux as its tech stack