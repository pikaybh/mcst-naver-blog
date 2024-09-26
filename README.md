# Naver Blog Scraper

This project is a Python-based web scraper for crawling blog posts from Naver's blog theme pages using [Playwright](https://playwright.dev/) and [asyncio](https://docs.python.org/3/library/asyncio.html). It scrapes blog post titles and content from multiple pages and saves the results into an Excel file.

## Features

- Scrapes multiple pages of blog posts from a specified Naver blog theme section.
- Extracts both the title and content of each blog post.
- Saves the scraped data to an Excel file with a timestamp.
- Handles pagination and retries in case of failures or timeouts.
- Uses a logging system to keep track of progress and errors.
- Supports both headless and non-headless browser modes for scraping.

## Prerequisites

To run this project, ensure you have the following installed:

- Python 3.7 or higher
- Playwright
- pandas
- tqdm
- fire

You can install the necessary Python packages with:

```bash
pip install playwright pandas tqdm fire
```

Additionally, you need to install the Playwright browsers:

```bash
playwright install
```

## Project Structure

```bash
│  .gitignore            # Git ignore file
│  crawl_naver_blogs.py  # Main blog scraping script
│
├─logs                  # Log files from the scraper
│      crawl_naver_blogs.log
│
├─output                # Output folder for scraped blog content
│      blog_contents.xlsx
│      blog_contents_20240926_154439.xlsx
│      blog_contents_20240926_173714.xlsx
│      blog_contents_20240926_184237.xlsx
│      blog_contents_preprocessed.xlsx
│
├─samples               # Placeholder for sample data or sample usage
│
└─utils
         decorators.py  # Utility functions like retry decorator
```

## How to Use

1. Clone the repository:

```bash
git clone https://github.com/pikaybh/mcst-naver-blog.git
cd your-repo
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the scraper:

You can run the script with customizable parameters using [fire](https://github.com/google/python-fire) to specify the number of pages to scrape and whether to use headless mode.

```bash
python crawl_naver_blogs.py --max_pages=50 --headless=True
```

### Parameters:

- `--max_pages`: The maximum number of pages to scrape (default: 10).
- `--headless`: Whether to run the scraper in headless mode (default: True).

### Example:

```bash
python crawl_naver_blogs.py --max_pages=20 --headless=False
```

This will scrape 20 pages from Naver's blog theme section and run the browser in non-headless mode (so you can see the browser window).

## Output

The scraped blog content is saved into Excel files in the `output/` directory. The file name will include a timestamp to help distinguish between different runs.

Example output:

```
output/blog_contents_20240926_184237.xlsx
```

## Author

- @pikaybh