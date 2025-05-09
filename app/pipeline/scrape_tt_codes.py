import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
import csv
from typing import Set
from pathlib import Path
from config import URL, TSV_FILENAME, MAX_CLICKS
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.logger import logger

async def extract_tt_codes(html: str) -> Set[str]:
    """
    Extracts IMDb tt codes from the provided HTML content.

    Args:
        html (str): The HTML content of the IMDb page.

    Returns:
        set: A set of unique tt codes extracted from the page.
    """
    soup = BeautifulSoup(html, "html.parser")
    movie_list = soup.find_all("li", {"class": "ipc-metadata-list-summary-item"})

    tt_codes = set()
    for movie in movie_list:
        link = movie.find("a", {"class": "ipc-title-link-wrapper", "href": True})
        if link:
            match = re.search(r"/title/(tt\d+)/", link["href"])
            if match:
                tt_codes.add(match.group(1))  # Extract tt_code
    return tt_codes


async def scrape_imdb_movie_codes() -> None:
    """
    Scrapes IMDb movie tt codes by navigating through the IMDb page and extracting tt codes.
    The extracted tt codes are saved to a TSV file.

    Steps:
        1. Opens the IMDb URL using Playwright.
        2. Extracts tt codes from the current page.
        3. Saves new tt codes to a TSV file.
        4. Clicks the "Show More" button to load additional movies and repeats the process.

    Raises:
        Exception: If any error occurs during the scraping process.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to True for headless mode
        page = await browser.new_page()

        # Load IMDb page
        logger.info(f"Opening {URL}")
        await page.goto(URL, timeout=120000)
        await asyncio.sleep(5)  # Wait for initial page load

        saved_codes = set()

        # Load existing codes from CSV
        if Path(TSV_FILENAME).exists():
            with open(TSV_FILENAME, "r", newline="") as file:
                reader = csv.reader(file, delimiter="\t")
                next(reader, None)
                saved_codes.update(row[0] for row in reader)

        # Open CSV for writing
        with open(TSV_FILENAME, "w", newline="") as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerow(["tconst"])

            click_attempts = 0

            while click_attempts < MAX_CLICKS:
                logger.info(f"Scraping Page {click_attempts + 1}...")

                # Extract tt_codes from the current page
                html = await page.content()
                new_tt_codes = await extract_tt_codes(html)

                # Save only new tt_codes
                unique_tt_codes = new_tt_codes - saved_codes
                if unique_tt_codes:
                    for code in unique_tt_codes:
                        writer.writerow([code])
                        saved_codes.add(code)
                    logger.info(f"Saved {len(unique_tt_codes)} new tt_codes to CSV.")

                # Try clicking "Show More" button
                try:
                    show_more_button = await page.wait_for_selector("button.ipc-see-more__button", timeout=5000)
                    if show_more_button:
                        logger.info("Clicking 'Show More' button...")
                        await show_more_button.scroll_into_view_if_needed()
                        await asyncio.sleep(1)  # Small delay before clicking
                        await show_more_button.click()
                        await asyncio.sleep(5)  # Wait for more movies to load
                    else:
                        logger.info("No more 'Show More' button found. Stopping scrape.")
                        break
                except:
                    logger.info("No more 'Show More' button detected.")
                    break

                click_attempts += 1

        await browser.close()
        logger.info("Scraping completed successfully!")


def run_scraper() -> None:
    """
    Runs the IMDb tt code scraper.

    This function initializes the asynchronous scraping process and ensures
    that the `scrape_imdb_movie_codes` coroutine is executed.
    """
    asyncio.run(scrape_imdb_movie_codes())

