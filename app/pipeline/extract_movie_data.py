import asyncio
import aiohttp
import ssl
import certifi
from typing import Union
from bs4.element import Tag
from bs4 import BeautifulSoup
import random
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from config import TSV_FILENAME, PROCESSED_IDS, OUTPUT_FILE
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.logger import logger

class IMDbCrawler:
    """
    An asynchronous web crawler for scraping IMDb movie metadata and synopses.

    Attributes:
        output_dir (Path): Directory to store output files.
        min_delay (float): Minimum delay between requests (for rate limiting).
        max_delay (float): Maximum delay between requests.
        max_retries (int): Number of retry attempts for failed requests.
        concurrent_requests (int): Maximum number of concurrent requests.
        headers (dict): HTTP headers to mimic browser behavior.
        session (aiohttp.ClientSession): Reusable HTTP session for requests.
    """
    def __init__(self, output_dir: str = "imdb_data",
                 min_delay: float = 2.0,
                 max_delay: float = 4.0,
                 max_retries: int = 3,
                 concurrent_requests: int = 3) -> None:

        # Initialize directory structure
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Set crawler parameters
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.concurrent_requests = concurrent_requests

        # Configure request headers to mimic browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,...',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        self.session = None

    async def init_session(self) -> None:
        """Initializes the aiohttp session with SSL context."""
        if not self.session:
            # Create SSL context with proper certificate verification
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            # Configure TCP connector with SSL settings
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                verify_ssl=True,
                force_close=True  # Ensure connections are closed after use
            )
            # Create the client session
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                connector=connector
            )

    async def get_movies_from_tsv(self, tsv_file: str = TSV_FILENAME) -> List[str]:
        """
        Reads movie IDs from a TSV file and filters out already processed IDs.

        Args:
            tsv_file (str): Path to the input TSV file.

        Returns:
            List[str]: List of IMDb movie IDs to process.
        """
        try:
            # Read the input TSV file
            df = pd.read_csv(tsv_file, sep='\t')
            # Check for and handle already processed movies
            processed_file = self.output_dir / PROCESSED_IDS
            if processed_file.exists():
                processed_df = pd.read_csv(processed_file, sep='\t')
                processed_ids = set(processed_df['tconst'].tolist())
                # Remove already processed movies from the queue
                df = df[~df['tconst'].isin(processed_ids)]
            logger.info(f"Found {len(df)} movies to process")
            return df['tconst'].tolist()
        except Exception as e:
            logger.info(f"Error reading TSV file: {e}")
            return []

    async def record_processed_id(self, tconst: str) -> None:
        """
        Records a processed IMDb ID into a TSV log with timestamp.

        Args:
            tconst (str): IMDb title ID.
        """
        processed_file = self.output_dir / PROCESSED_IDS
        try:
            # Create DataFrame with movie ID and timestamp
            df = pd.DataFrame({
                'tconst': [tconst],
                'processed_time': [datetime.now().isoformat()]
            })
            # Append or create the processed IDs file
            if processed_file.exists():
                df.to_csv(processed_file, mode='a', header=False, index=False, sep='\t')
            else:
                df.to_csv(processed_file, index=False, sep='\t')
        except Exception as e:
            logger.info(f"Error recording processed ID: {e}")

    async def extract_movie_data(self, tconst: str) -> Dict[str, Union[str, List[str], None]]:
        """
        Extracts full metadata and synopsis info from IMDb for a single title.

        Args:
            tconst (str): IMDb title ID.

        Returns:
            Dict: Extracted movie data.
        """
        # Initialize movie data structure with metadata
        movie_data = {
            'tconst': tconst,
            'crawl_timestamp': datetime.now().isoformat()
        }
        # Construct main movie page URL
        if not tconst.startswith('/title/'):
            main_url = f"https://www.imdb.com/title/{tconst}/"
        else:
            main_url = f"https://www.imdb.com{tconst}"
        logger.info(f"Fetching movie data from: {main_url}")
        try:
            # Fetch and process main page
            async with self.session.get(main_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    # Extract all available data points
                    movie_data.update({
                        'movie_title': self._extract_title(soup),
                        'movie_year': self._extract_year(soup, tconst),
                        'age_rating': self._extract_age_rating(soup, tconst),
                        'duration': self._extract_runtime(soup),
                        'imdb_rating': self._extract_imdb_rating(soup),
                        'short_synopsis': self._extract_short_synopsis(soup),
                        'top_5_actors': self._extract_top_actors(soup),
                        'genres': self._extract_genres(soup),
                        'poster_url': self._extract_poster_url(soup),
                        'summaries': self._extract_summaries(soup),
                        'long_synopsis': self._extract_long_synopsis(soup),
                    })
                    # Implement rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                else:
                    logger.info(f"Failed to get movie {tconst}: Status {response.status}")
        except Exception as e:
            logger.info(f"Error extracting main data for {tconst}: {str(e)}")
        # Fetch and process plot summary page
        plot_url = f"https://www.imdb.com/title/{tconst}/plotsummary/"
        try:
            async with self.session.get(plot_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    movie_data['long_synopsis'] = self._extract_long_synopsis(soup)
                    movie_data['summaries'] = self._extract_summaries(soup)
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
        except Exception as e:
            logger.info(f"Error extracting plot data for {tconst}: {str(e)}")
        return movie_data

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extracts the movie title from the given HTML soup.

        Args:
            soup (BeautifulSoup): Parsed IMDb movie page.

        Returns:
            Optional[str]: Extracted movie title or default fallback.
        """
        try:
            # IMDb page structures can change, so we use multiple selector strategies
            title_tag = soup.find("span", {"data-testid": "hero__primary-text"})
            # Extract and return the title if found
            return title_tag.get_text(strip=True) if title_tag else "Title not found"
        except Exception as e:
            logger.info(f"Error extracting title: {e}")
            return None

    def _extract_long_synopsis(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extracts the long synopsis from the movie's IMDb plot page.

        Args:
            soup (BeautifulSoup): Parsed IMDb plot page HTML.

        Returns:
            Optional[str]: Full synopsis text or fallback message.
        """
        try:
            # Locate the full synopsis section
            synopsis_section = soup.find("div", {"data-testid": "sub-section-synopsis"})
            # Extract the full synopsis text if available
            movie_synopsis = (
                synopsis_section.find("div", {"class": "ipc-html-content-inner-div", "role": "presentation"}).get_text(
                    strip=True)
                if synopsis_section else "Synopsis not found"
            )
            return movie_synopsis
        except Exception as e:
            logger.info(f"Error extracting long synopsis: {e}")
            return None

    def _extract_year(self, soup: BeautifulSoup, tconst: str) -> Optional[str]:
        """
        Extracts the movie release year using the IMDb releaseinfo URL.

        Args:
            soup (BeautifulSoup): Parsed IMDb movie page.
            tconst (str): IMDb title ID.

        Returns:
            Optional[str]: Release year or fallback message.
        """
        try:
            # Generate the release info URL dynamically based on tconst
            release_info_href = f"/title/{tconst}/releaseinfo"
            # Find the anchor tag that links to the release info page
            year_tag = soup.find("a", {"class": "ipc-link ipc-link--baseAlt ipc-link--inherit-color"},
                                 href=lambda x: x and release_info_href in x)
            # Extract and return the year if found
            return year_tag.get_text(strip=True) if year_tag else "Year not found"
        except Exception as e:
            logger.info(f"Error extracting year for {tconst}: {e}")
            return None

    def _extract_age_rating(self, soup: BeautifulSoup, tconst: str) -> Optional[str]:
        """
        Extracts the parental age rating.

        Args:
            soup (BeautifulSoup): Parsed IMDb movie page.
            tconst (str): IMDb title ID.

        Returns:
            Optional[str]: Age rating or fallback message.
        """
        try:
            # Generate the parental guide URL dynamically based on tconst
            parental_guide_href = f"/title/{tconst}/parentalguide"
            # Find the anchor tag that links to the parental guide page
            rating_tag = soup.find("a", {"class": "ipc-link ipc-link--baseAlt ipc-link--inherit-color"},
                                   href=lambda x: x and parental_guide_href in x)
            # Extract and return the age rating if found
            return rating_tag.get_text(strip=True) if rating_tag else "Rating not found"
        except Exception as e:
            logger.info(f"Error extracting age rating for {tconst}: {e}")
            return None

    def _extract_runtime(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extracts the movie runtime.

        Args:
            soup (BeautifulSoup): Parsed IMDb movie page.

        Returns:
            Optional[str]: Runtime string or fallback.
        """
        try:
            # Locate the runtime metadata section
            runtime_tag = soup.find("li", {"role": "presentation", "class": "ipc-metadata-list__item",
                                           "data-testid": "title-techspec_runtime"})
            # Extract runtime from the correct div container
            if runtime_tag:
                runtime_span = runtime_tag.find("div", {"class": "ipc-metadata-list-item__content-container"})
                return runtime_span.get_text(strip=True) if runtime_span else "Runtime not found"
            return "Runtime not found"
        except Exception as e:
            logger.info(f"Error extracting runtime: {e}")
            return None

    def _extract_imdb_rating(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extracts the IMDb rating of the movie.

        Args:
            soup (BeautifulSoup): Parsed IMDb movie page.

        Returns:
            Optional[str]: IMDb rating or fallback.
        """
        try:
            # Locate the IMDb rating section
            rating_tag = soup.find("div", {"data-testid": "hero-rating-bar__aggregate-rating__score",
                                           "class": "sc-d541859f-2 kxphVf"})
            # Extract rating from the correct span container
            if rating_tag:
                rating_span = rating_tag.find("span", {"class": "sc-d541859f-1 imUuxf"})
                return rating_span.get_text(strip=True) if rating_span else "Rating not found"
            return "Rating not found"
        except Exception as e:
            logger.info(f"Error extracting IMDb rating: {e}")
            return None

    def _extract_top_actors(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts the top 5 actors listed in the cast section.

        Args:
            soup (BeautifulSoup): Parsed IMDb movie page.

        Returns:
            List[str]: Actor names or fallback.
        """
        try:
            # Locate the actors section
            actors_section = soup.find("div",
                                       {"class": "ipc-shoveler ipc-shoveler--base ipc-shoveler--page0 title-cast__grid",
                                        "role": "group", "data-testid": "shoveler"})
            # Extract all actor items
            actors = []
            if actors_section:
                actor_items = actors_section.find_all("a", {"data-testid": "title-cast-item__actor"})
                actors = [actor.get_text(strip=True) for actor in actor_items[:5]]  # Extract top 5 actors
            return actors if actors else ["Actors not found"]
        except Exception as e:
            logger.info(f"Error extracting actors: {e}")
            return ["Actors not found"]

    def _extract_genres(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts the list of genres from the IMDb movie page.

        Args:
            soup (BeautifulSoup): Parsed IMDb movie page.

        Returns:
            List[str]: Genres or fallback.
        """
        try:
            # Locate the genre section
            genre_section = soup.find("div", {"class": "ipc-chip-list__scroller"})
            # Extract all genre items
            genres = []
            if genre_section:
                genre_items = genre_section.find_all("span")  # Adjust based on structure
                genres = [genre.get_text(strip=True) for genre in genre_items]
            return genres if genres else ["Genres not found"]
        except Exception as e:
            logger.info(f"Error extracting genres: {e}")
            return ["Genres not found"]

    def _extract_poster_url(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extracts the movie poster image URL.

        Args:
            soup (BeautifulSoup): Parsed IMDb movie page.

        Returns:
            Optional[str]: Poster URL or fallback.
        """
        try:
            # Locate the poster container
            poster_container = soup.find("div", {
                "class": "ipc-media ipc-media--poster-27x40 ipc-image-media-ratio--poster-27x40 ipc-media--media-radius ipc-media--baseAlt ipc-media--poster-l ipc-poster__poster-image ipc-media__img"})
            # Extract image tag and its URL
            if poster_container:
                img_tag = poster_container.find("img")
                return img_tag['src'] if img_tag and img_tag.has_attr('src') else "Poster not found"
            return "Poster not found"
        except Exception as e:
            logger.info(f"Error extracting poster URL: {e}")
            return None

    def _extract_short_synopsis(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extracts the short synopsis (1-line summary).

        Args:
            soup (BeautifulSoup): Parsed IMDb movie page.

        Returns:
            Optional[str]: Short synopsis or fallback.
        """
        try:
            # Locate the short synopsis section
            synopsis_tag = soup.find("span", {"role": "presentation", "data-testid": "plot-l", "class":"sc-191592d9-1 kBRZRe"})
            # Extract and return the short synopsis
            return synopsis_tag.get_text(strip=True) if synopsis_tag else "No short sum found"
        except Exception as e:
            logger.info(f"Error extracting short synopsis: {e}")
            return None

    def _extract_summaries(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts a list of user-submitted plot summaries.

        Args:
            soup (BeautifulSoup): Parsed IMDb plot summary page.

        Returns:
            List[str]: Plot summaries or fallback.
        """
        try:
            summaries_section = soup.find("div", {"data-testid": "sub-section-summaries"})

            summaries = []
            if summaries_section:
                summary_items = summaries_section.find_all("li")  # Adjust based on IMDb structure
                summaries = [summary.get_text(strip=True) for summary in summary_items]

            return summaries if summaries else ["No summaries found"]
        except Exception as e:
            logger.info(f"Error extracting summaries: {e}")
            return ["No summaries found"]

    def _extract_text(self, element: Optional[Tag]) -> Optional[str]:
        """
        Extracts text from a BeautifulSoup element.

        Args:
            element (Tag): A BeautifulSoup element.

        Returns:
            Optional[str]: Cleaned text or None.
        """
        return element.get_text(strip=True) if element else None

    async def crawl_movies(self, num_movies: Optional[int] = None) -> None:
        """
        Orchestrates crawling multiple IMDb movies concurrently and writes results to CSV in batches.

        Args:
            num_movies (int, optional): Maximum number of movies to crawl. Defaults to all.
        """
        try:
            await self.init_session()
            logger.info(f"Reading movie IDs from TSV...")
            movie_ids = await self.get_movies_from_tsv()
            if not movie_ids:
                logger.info("No movies found in TSV!")
                return
            # Apply optional movie limit
            if num_movies:
                movie_ids = movie_ids[:num_movies]
            logger.info(f"Found {len(movie_ids)} movies to crawl")
            # Set up concurrency control
            semaphore = asyncio.Semaphore(self.concurrent_requests)
            all_movie_data = []  # Temporary storage for batch processing
            csv_file = self.output_dir / OUTPUT_FILE
            # Track CSV file existence for header management
            self.csv_exists = csv_file.exists()

            async def crawl_with_semaphore(tcont):
                nonlocal all_movie_data
                async with semaphore:
                    movie_data = await self.extract_movie_data(tcont)
                    if movie_data:
                        all_movie_data.append(movie_data)
                        await self.record_processed_id(tcont)
                        # Batch write to CSV every 100 movies
                        if len(all_movie_data) >= 100:
                            df = pd.DataFrame(all_movie_data)
                            if self.csv_exists:
                                df.to_csv(csv_file, mode='a', header=False, index=False)
                            else:
                                df.to_csv(csv_file, index=False)
                                self.csv_exists = True
                            all_movie_data.clear()
                            logger.info(f"Wrote batch of {len(df)} movies to CSV")
            # Create and execute crawling tasks
            tasks = [crawl_with_semaphore(tcont) for tcont in movie_ids]
            # Monitor progress
            for i, task in enumerate(asyncio.as_completed(tasks)):
                await task
                logger.info(f"Progress: {i + 1}/{len(movie_ids)} movies processed")
            # Handle any remaining movies in the batch
            if all_movie_data:
                df = pd.DataFrame(all_movie_data)
                if self.csv_exists:
                    df.to_csv(csv_file, mode='a', header=False, index=False)
                else:
                    df.to_csv(csv_file, index=False)
                logger.info(f"Wrote final batch of {len(df)} movies to CSV")
        except Exception as e:
            logger.info(f"Error during crawling: {str(e)}")
        finally:
            await self.close_session()

    async def close_session(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Session closed.")


async def run_crawler(output_dir: str = "imdb_data", tsv_file: Optional[str] = None, num_movies: int = 0) -> None:
    """
    Entrypoint to run the IMDbCrawler with optional input and batch limits.

    Args:
        output_dir (str): Output directory path.
        tsv_file (str, optional): Path to custom TSV file of movie IDs.
        num_movies (int): Number of movies to crawl (0 = all).
    """
    try:
        crawler = IMDbCrawler(
            output_dir=output_dir,
            min_delay=2.0,
            max_delay=4.0,
            concurrent_requests=3
        )
        if tsv_file:
            crawler.tsv_file = tsv_file  # Optional override
        await crawler.crawl_movies(num_movies=num_movies)
        logger.info("Movie crawl complete.")
    except Exception as e:
        logger.info(f"Error running crawler: {e}")
    finally:
        if crawler.session:
            await crawler.close_session()