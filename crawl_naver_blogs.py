from utils.decorators import retry
from playwright.async_api import async_playwright, Page, TimeoutError
from tqdm.asyncio import tqdm
from typing import Dict, List
import pandas as pd
import datetime
import asyncio
import logging
import fire


# Logger setup
logger_name = "crawl_naver_blogs"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)
# File Handler
file_handler = logging.FileHandler(f'logs/{logger_name}.log', encoding='utf-8-sig')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(r'%(asctime)s [%(name)s, line %(lineno)d] %(levelname)s: %(message)s'))
logger.addHandler(file_handler)
# Stream Handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter(r'%(message)s'))
logger.addHandler(stream_handler)

class BlogScraper:
    def __init__(self, initial_page: int = 1, max_pages: int = 10, headless: bool = True):
        """
        BlogScraper constructor

        Args:
            max_pages (int): Maximum number of pages to scrape.
            headless (bool): Whether to run the browser in headless mode.
        """
        self.max_pages = max_pages
        self.headless = headless
        self.current_page = initial_page
        self.blog_contents = []

    @retry(max_retries=10, delay=5, exceptions=(ValueError, TimeoutError))
    async def scrape_blog_content(self, page: Page, blog_url: str) -> Dict[str, str]:
        """
        Scrapes individual blog post content.

        Args:
            page (Page): Playwright Page object.
            blog_url (str): The URL of the blog post to scrape.

        Returns:
            Dict[str, str]: Dictionary containing the title and content of the blog post.
        """
        await page.goto(blog_url)
        await page.wait_for_load_state('networkidle')  # Wait until the page is fully loaded
        logger.debug(f"Current URL: {page.url}\tCurrent page: {self.current_page}")
        
        title = await page.locator('title').inner_text()

        try:
            frame = page.frame(name="mainFrame")  # Access iframe for content

            paragraphs = await frame.locator('p span.se-fs-').all()
            content = [await span.inner_text() for span in paragraphs]
            
            if not content:
                logger.warning(f"No content found for {blog_url}")
                content = ["No content found"]
        except Exception as e:
            logger.error(f"Error occurred while scraping {blog_url}: {e}")
            content = ["No content found"]

        article_content = '\n'.join(content).strip() if len(content) > 1 else "No content found"
        logger.debug(f"Scraped: {title}, {article_content}")
        
        return {"title": title, "content": article_content}

    async def scrape_blog_links(self, page: Page) -> List[str]:
        """
        Scrapes blog post links from a theme page.

        Args:
            page (Page): Playwright Page object.

        Returns:
            List[str]: List of blog post URLs.
        """
        blog_links = []
        posts = await page.locator('a.desc_inner').all()
        for post in posts:
            blog_url = await post.get_attribute('href')
            blog_links.append(blog_url)
        logger.debug(f"Found {len(blog_links)} blog links.")
        return blog_links

    @property
    def theme_post_link(self) -> str:
        """
        Property that generates the URL for the current page number in the theme post section.

        Returns:
            str: The URL for the current page.
        """
        return f'https://section.blog.naver.com/ThemePost.naver?directoryNo=27&activeDirectorySeq=3&currentPage={self.current_page}'


    async def run(self) -> None:
        """
        Main runner function for the BlogScraper.

        - Launches the browser.
        - Scrapes blog links and content from the specified number of pages.
        - Saves the content to an Excel file.
        """
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            current_page = 1

            while current_page <= self.max_pages:
                # Log the current URL being scraped
                logger.info(f"Scraping page {current_page}")
                logger.info(f"Scraping URL: {self.theme_post_link}")

                # Navigate to the current page
                await page.goto(self.theme_post_link)
                
                # Wait for blog links to load (ensure that content is fully rendered)
                await page.wait_for_selector('a.desc_inner', timeout=10_000)  # Adjust selector and timeout as needed

                # Scrape blog links on the current page
                blog_links = await self.scrape_blog_links(page)
                logger.info(f"Found {len(blog_links)} blog links on page {current_page}")
                
                # If no links are found, log an error and break
                if len(blog_links) == 0:
                    logger.error(f"No blog links found on page {current_page}. Stopping scraper.")
                    break

                # Scrape content for each blog post
                for blog_url in tqdm(blog_links, desc=f"Scraping posts from page {current_page}"):
                    result = await self.scrape_blog_content(page, blog_url)
                    self.blog_contents.append({"Title": result["title"], "Content": result["content"]})
                
                # Move to the next page
                current_page += 1

            # Save results to Excel
            self.save_to_excel()

            # Close the browser
            await browser.close()


    def save_to_excel(self):
        """
        Saves the scraped blog content to an Excel file with a timestamp.
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        df = pd.DataFrame(self.blog_contents)
        df.to_excel(f'output/blog_contents_{timestamp}.xlsx', index=False)
        logger.info(f"Saved blog contents to output/blog_contents_{timestamp}.xlsx")


def main(max_pages: int = 10, headless: bool = True):
    """
    Main entry point for the blog scraper.

    Args:
        max_pages (int): Maximum number of pages to scrape.
        headless (bool): Whether to run the browser in headless mode.
    """
    scraper = BlogScraper(max_pages=max_pages, headless=headless)
    asyncio.run(scraper.run())


# Use Fire to make the script executable from the command line with arguments
if __name__ == "__main__":
    fire.Fire(main)
