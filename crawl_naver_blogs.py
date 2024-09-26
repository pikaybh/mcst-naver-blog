# Internal Modules
from utils.decorators import retry
# External Modules
from playwright.async_api import async_playwright, Page
from tqdm.asyncio import tqdm
from typing import Dict, List
import pandas as pd
import asyncio
import logging

# Root 
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


# 함수 정의: 개별 블로그 포스트의 제목과 내용을 추출하는 함수
@retry(max_retries=10, delay=5, exceptions=(ValueError, TimeoutError))
async def scrape_blog_content(page: Page, blog_url: str) -> Dict[str, str]:
    """
    개별 블로그 포스트에서 제목과 내용을 추출하는 비동기 함수.
    
    Args:
        page (Page): Playwright의 페이지 객체, 블로그 포스트로 이동하기 위해 사용됩니다.
        blog_url (str): 추출할 블로그 포스트의 URL.

    Returns:
        Dict[str, str]: 추출한 블로그 포스트 제목과 내용. 실패 시 빈 제목과 "No content found" 반환.
    """
    await page.goto(blog_url)
    await page.wait_for_load_state('networkidle')  # 페이지가 완전히 로드될 때까지 대기
    logger.debug(f"Current URL: {page.url}")
        
    # 제목 추출
    title = await page.locator('title').inner_text()

    try:
        # iframe에 접근
        frame = page.frame(name="mainFrame")

        # 모든 <p> 태그 내 <span> 태그의 텍스트를 개별적으로 추출하여 리스트에 저장
        paragraphs = await frame.locator('p span.se-fs-').all()
        content = [await span.inner_text() for span in paragraphs]
        
        if not content:  # content 리스트가 비어 있을 경우
            logger.warning(f"No content found for {blog_url}")
            content = ["No content found"]
    except Exception as e:
        logger.error(f"Error occurred while scraping {blog_url}: {e}")
        content = ["No content found"]
    logger.debug(f"{title = }")
    logger.debug(f"{content = }")
    
    # 리스트의 첫 번째 요소를 제목으로 설정, 내용은 전체를 이어붙임
    article_content = '\n'.join(content).strip() if len(content) > 1 else "No content found"
    
    logger.debug(f"Scraped: {title}, {article_content}")
    return {"title": title, "content": article_content}




# 함수 정의: 메인 페이지에서 블로그 링크를 추출하는 함수
async def scrape_blog_links(page: Page) -> List[str]:
    """
    블로그 테마 페이지에서 개별 블로그 포스트의 링크를 추출하는 비동기 함수.

    Args:
        page (Page): Playwright의 페이지 객체, 테마 포스트로 이동하기 위해 사용됩니다.

    Returns:
        List[str]: 추출한 블로그 포스트 링크들의 리스트.
    """
    await page.goto('https://section.blog.naver.com/ThemePost.naver?directoryNo=27&activeDirectorySeq=3&currentPage=1')
    blog_links = []
    
    # 해당 태그를 가진 링크들을 찾습니다.
    posts = await page.locator('a.desc_inner').all()
    for post in posts:
        blog_url = await post.get_attribute('href')
        blog_links.append(blog_url)
    logger.debug(f"Found {len(blog_links)} blog links.")
    return blog_links


# 메인 함수
async def main() -> None:
    """
    Playwright를 사용하여 블로그 테마 포스트의 링크를 추출하고,
    각 링크에서 포스트 제목과 내용을 수집한 뒤 엑셀 파일로 저장하는 비동기 함수.
    """
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 블로그 링크들을 가져옵니다.
        blog_links = await scrape_blog_links(page)

        # 각 블로그 링크를 방문하여 제목과 내용을 추출합니다.
        blog_contents = []
        for blog_url in tqdm(blog_links, desc="블로그 포스트 스크래핑 중"):
            result = await scrape_blog_content(page, blog_url)
            blog_contents.append({"Title": result["title"], "Content": result["content"]})
        
        # DataFrame으로 변환 후 엑셀 파일로 저장합니다.
        df = pd.DataFrame(blog_contents)
        df.to_excel('output/blog_contents.xlsx', index=False)

        # 브라우저 종료
        await browser.close()

# Playwright는 비동기이므로 asyncio.run으로 실행합니다.
asyncio.run(main())
