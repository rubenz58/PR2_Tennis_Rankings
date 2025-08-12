# RUN FROM PROJECT ROOT
# python -m scripts.populate_initial_data

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import os

from models import Player, db
# Have to have an application context in order to connect to DB
# create_app()
# Flask-SQLAlchemy requires an application context to know:
# Which db to connect to, connection settings, how to handle transactions
from app import create_app


# Ranking
# <td class="rank bold heavy tiny-cell" colspan="2">1</td>

# Name
# <li class="name">
#     <a href="/en/players/jannik-sinner/s0ag/overview">
#         <span class="lastName">J. Sinner</span>
#     </a>
# </li>

# Points
# <td class="points center bold extrabold small-cell" colspan="3">
#     <a href="/en/players/jannik-sinner/s0ag/rankings-breakdown?team=singles">
#         12,030
#     </a>
# </td>

# 4 functions.
# main(): Run everything
# fetch_atp_rankings(): Gets the players
# parse_rankings_html(): parses for information
# add_to_db(): Adds players to DB


def fetch_atp_rankings():
    url = 'https://www.atptour.com/en/rankings/singles'
    
    try:
        print(f"Setting up Chrome browser...")
        
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run without opening browser window
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Setup ChromeDriver (webdriver-manager handles download automatically)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"Navigating to: {url}")
        driver.get(url)
        
        # Wait for Cloudflare to pass and page to load
        print("Waiting for Cloudflare challenge to complete...")
        time.sleep(10)  # Give it time to pass Cloudflare
        
        # Check if we're still on Cloudflare page
        if "Just a moment" in driver.page_source or "challenge" in driver.current_url:
            print("Still on Cloudflare challenge page, waiting longer...")
            time.sleep(15)
        
        print("Getting page source...")
        html_content = driver.page_source
        
        # Save HTML for debugging
        with open('atp_rankings_selenium.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("HTML saved to atp_rankings_selenium.html for debugging")
        
        driver.quit()
        
        return parse_rankings_html(html_content)
        
    except Exception as e:
        print(f"Error fetching ATP rankings: {e}")
        if 'driver' in locals():
            driver.quit()
        return []
    

def parse_rankings_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    players_data = []
    
    print("Parsing HTML content...")
    
    # First, let's find the actual structure by looking for ranking data
    # ATP might use different selectors, so we'll try multiple approaches
    
    # Try approach 1: Look for table rows
    ranking_rows = soup.find_all('tr')
    if ranking_rows:
        print(f"Found {len(ranking_rows)} table rows, attempting to parse...")
        players_data = parse_table_structure(ranking_rows)
    
    # If no data found, try approach 2: Look for div-based structure
    if not players_data:
        print("No data in table rows, trying div-based structure...")
        ranking_divs = soup.find_all('div', class_=lambda x: x and 'player' in x.lower())
        if ranking_divs:
            print(f"Found {len(ranking_divs)} player divs, attempting to parse...")
            players_data = parse_div_structure(ranking_divs)
    
    # If still no data, print some debug info
    if not players_data:
        print("No ranking data found. Debug info:")
        print(f"Page title: {soup.title.get_text() if soup.title else 'No title'}")
        print(f"Page contains 'rankings': {'rankings' in html_content.lower()}")
        print(f"Page contains 'player': {'player' in html_content.lower()}")
        
        # Print first 1000 characters for debugging
        print("First 1000 characters of page:")
        print(html_content[:1000])
    
    print(f"\nSuccessfully parsed {len(players_data)} players")
    return players_data

def parse_table_structure(rows):
    """
    Try to parse table-based ranking structure
    """
    players_data = []
    
    for row in rows:
        try:
            # Look for rank
            rank_cell = row.find('td', class_=lambda x: x and 'rank' in x.lower())
            if not rank_cell:
                continue
            
            rank_text = rank_cell.get_text(strip=True)
            if not rank_text.isdigit():
                continue
            rank = int(rank_text)
            
            # Look for name - try multiple selectors
            name = None
            name_selectors = [
                'li.name span.lastName',
                'td .player-name',
                'td .name',
                '.lastName'
            ]
            
            for selector in name_selectors:
                name_element = row.select_one(selector)
                if name_element:
                    name = name_element.get_text(strip=True)
                    break
            
            if not name:
                continue
            
            # Look for points
            points = None
            points_selectors = [
                'td.points',
                'td .points',
                '.points'
            ]
            
            for selector in points_selectors:
                points_element = row.select_one(selector)
                if points_element:
                    points_text = points_element.get_text(strip=True)
                    # Remove commas and convert to integer
                    points = int(points_text.replace(',', '').replace('.', ''))
                    break
            
            if points is None:
                continue
            
            player_data = {
                'rank': rank,
                'name': name,
                'points': points
            }
            
            players_data.append(player_data)
            print(f"Parsed: #{rank} {name} - {points:,} points")
            
        except (ValueError, AttributeError) as e:
            continue
    
    return players_data

def parse_div_structure(divs):
    """
    Try to parse div-based ranking structure
    """
    players_data = []
    
    for div in divs:
        try:
            # Look for rank, name, and points within the div
            rank_element = div.find(class_=lambda x: x and 'rank' in x.lower())
            name_element = div.find(class_=lambda x: x and 'name' in x.lower())
            points_element = div.find(class_=lambda x: x and 'point' in x.lower())
            
            if not all([rank_element, name_element, points_element]):
                continue
            
            rank_text = rank_element.get_text(strip=True)
            if not rank_text.isdigit():
                continue
            rank = int(rank_text)
            
            name = name_element.get_text(strip=True)
            
            points_text = points_element.get_text(strip=True)
            points = int(points_text.replace(',', '').replace('.', ''))
            
            player_data = {
                'rank': rank,
                'name': name,
                'points': points
            }
            
            players_data.append(player_data)
            print(f"Parsed: #{rank} {name} - {points:,} points")
            
        except (ValueError, AttributeError) as e:
            continue
    
    return players_data


def main():
    print("=== ATP Rankings Scraper ===")
    print("Starting initial data population...\n")

    # Run once to save
    print("=== ATP Rankings Scraper (with Selenium) ===")
    print("Starting initial data population...\n")
    
    # Option 1: Use saved HTML file (for testing parsing logic)
    html_file = 'scripts/rankings_html/atp_rankings_selenium.html'
    
    if os.path.exists(html_file):
        print(f"Using saved HTML file: {html_file}")
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        players_data = parse_rankings_html(html_content)
    else:
        print(f"HTML file {html_file} not found. Fetching live data...")
        # Option 2: Fetch live data with Selenium
        # players_data = fetch_atp_rankings()
    
    if not players_data:
        print("No player data found. Check the saved HTML file for debugging.")
        return


if __name__ == '__main__':
    main()
