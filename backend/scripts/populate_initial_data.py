# RUN FROM PROJECT ROOT
# python -m scripts.populate_initial_data

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

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


# Tests on already saved data
def test_parsing():
    with open('atp_rankings.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    players_data = parse_rankings_html(html_content)
    print(f"Found {len(players_data)} players")
    return players_data


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

    ranking_rows = soup.find_all('tr')  # Assuming table rows contain the data



def main():
    print("=== ATP Rankings Scraper ===")
    print("Starting initial data population...\n")

    # Run once to save
    fetch_atp_rankings()
    
    # Fetch and parse rankings
    # players_data = fetch_atp_rankings()

    # if not players_data:
    #     print("No player data found. Exiting.")
    #     return
    
    # print(players_data)

    # print("\n=== Data population complete! ===")

if __name__ == '__main__':
    main()
