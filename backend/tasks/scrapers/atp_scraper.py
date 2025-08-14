"""
ATP Rankings Scraper for weekly updates
Handles scraping, parsing, and database updates
"""

import time
import logging
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from models import Player, db

# Configure logging
logger = logging.getLogger('scraping')

def scrape_and_update_rankings():
    """
    Main function called by scheduler
    Returns True if successful, False if failed
    """
    logger.info("=== Starting weekly ATP rankings update ===")
    start_time = datetime.now()

    
    try:
        # Step 1: Scrape the data
        logger.info("Fetching ATP rankings data...")
        players_data = fetch_atp_rankings()
        
        if not players_data:
            logger.error("SCRAPE FAILED: No player data retrieved")
            return False
        
        logger.info(f"SCRAPE SUCCESS: Retrieved {len(players_data)} players")
        
        # Step 2: Update database (only if scraping was successful)
        logger.info("Updating database...")
        update_database(players_data)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"=== UPDATE COMPLETED SUCCESSFULLY in {execution_time:.1f}s ===")

        # Log summary
        top_3 = players_data[:3] if len(players_data) >= 3 else players_data
        summary = " | ".join([f"#{p['rank']} {p['name']} ({p['points']})" for p in top_3])
        logger.info(f"Top 3: {summary}")

        return True
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"UPDATE FAILED after {execution_time:.1f}s: {str(e)}", exc_info=True)
        return False

def fetch_atp_rankings():
    """
    Scrape ATP rankings using Selenium
    Returns list of player dictionaries or empty list if failed
    """
    logger.info("Setting up Chrome browser for scraping...")


    url = 'https://www.atptour.com/en/rankings/singles'
    driver = None
    
    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Setup ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info(f"Navigating to: {url}")
        driver.get(url)
        
        # Wait for Cloudflare and page load
        logger.info("Waiting for page to load...")
        time.sleep(10)
        
        # Check if still on Cloudflare page
        if "Just a moment" in driver.page_source or "challenge" in driver.current_url:
            logger.warning("Still on Cloudflare challenge, waiting longer...")
            time.sleep(15)
        
        logger.info("Successfully bypassed Cloudflare protection")
        html_content = driver.page_source
        logger.info("Page content retrieved successfully")
        
        # Parse the HTML
        players_data = parse_rankings_html(html_content)
        logger.info(f"HTML parsing completed: {len(players_data)} players extracted")
        return players_data
        
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        return []
    finally:
        if driver:
            driver.quit()
            logger.info("Browser session closed")


def parse_rankings_html(html_content):
    """
    Parse HTML content and extract player data
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    players_data = []
    
    logger.info("Parsing HTML content...")
    
    # Find ranking rows (try table structure first)
    ranking_rows = soup.find_all('tr')
    
    for row in ranking_rows:
        try:
            # Extract ranking
            rank_cell = row.find('td', class_=lambda x: x and 'rank' in x.lower())
            if not rank_cell:
                continue
            
            rank_text = rank_cell.get_text(strip=True)
            if not rank_text.isdigit():
                continue
            rank = int(rank_text)
            
            # Extract name
            name_element = row.find('li', class_='name')
            if not name_element:
                continue
            
            name_span = name_element.find('span', class_='lastName')
            if not name_span:
                continue
            name = name_span.get_text(strip=True)
            
            # Extract points
            points_cell = row.find('td', class_=lambda x: x and 'point' in x.lower())
            if not points_cell:
                continue
            
            points_text = points_cell.get_text(strip=True)
            points = int(points_text.replace(',', '').replace('.', ''))
            
            players_data.append({
                'rank': rank,
                'name': name,
                'points': points
            })
            
        except (ValueError, AttributeError):
            continue
    
    # Remove duplicates and ensure we have valid data
    seen_ranks = set()
    unique_players = []
    for player in players_data:
        if player['rank'] not in seen_ranks and 1 <= player['rank'] <= 100:
            unique_players.append(player)
            seen_ranks.add(player['rank'])
    
    logger.info(f"Parsed {len(unique_players)} unique players")
    return unique_players

def update_database(players_data):
    """
    Update database with new rankings data
    Uses replace strategy for simplicity
    """
    logger.info("Starting database transaction...")

    try:
        # Get current count before deletion
        current_count = Player.query.count()
        logger.info(f"Current database contains {current_count} players")

        # Clear existing data
        Player.query.delete()
        logger.info(f"Deleted {current_count} existing records")
        
        # Insert new data
        for player_data in players_data:
            player = Player(
                ranking=player_data['rank'],
                name=player_data['name'],
                points=player_data['points'],
                last_updated=datetime.now(timezone.utc)
            )
            db.session.add(player)
        
        # Commit transaction
        db.session.commit()
        logger.info(f"Successfully inserted {len(players_data)} new records")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database update failed: {str(e)}")
        raise