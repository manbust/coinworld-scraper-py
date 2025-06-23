# scraper.py
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from selenium_stealth import stealth

def parse_currency(text: str) -> float:
    """
    Parses currency strings like '$52.0M', '$19.4K', or '1,234.56' into a float.
    Handles commas, '$' sign, and K/M/B/T suffixes.
    """
    if not text:
        return 0.0
    
    # Remove '$' and commas, then strip any leading/trailing whitespace
    cleaned_text = text.replace('$', '').replace(',', '').strip()
    
    if not cleaned_text: # If only symbols or whitespace were present
        return 0.0

    multiplier = 1.0
    
    # Check for suffixes (K, M, B, T) and adjust multiplier
    if cleaned_text.endswith('T'):
        multiplier = 1_000_000_000_000
        cleaned_text = cleaned_text[:-1]
    elif cleaned_text.endswith('B'):
        multiplier = 1_000_000_000
        cleaned_text = cleaned_text[:-1]
    elif cleaned_text.endswith('M'):
        multiplier = 1_000_000
        cleaned_text = cleaned_text[:-1]
    elif cleaned_text.endswith('K'):
        multiplier = 1_000
        cleaned_text = cleaned_text[:-1]
        
    try:
        # Convert the cleaned text to float and apply the multiplier
        return float(cleaned_text) * multiplier
    except ValueError:
        # If conversion fails (e.g., text is not a valid number), return 0.0
        print(f"Warning: Could not parse '{text}' (cleaned to '{cleaned_text}') into float in parse_currency.")
        return 0.0

def scrape_trending_tokens(chain: str) -> list:
    """
    Scrapes the trending tokens from Dexscreener for a given chain
    using a stealth-configured Selenium WebDriver.
    """
    print(f"Setting up Selenium WebDriver for chain: {chain}...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Apply stealth settings
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    scraped_tokens = []
    try:
        url = f"https://dexscreener.com/?rankBy=trendingScoreH6&order=desc&chainIds={chain}"
        print(f"Navigating to {url}")
        driver.get(url)

        # Wait for the table rows to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.ds-dex-table-row"))
        )
        print("Page loaded. Scraping rows...")
        
        rows = driver.find_elements(By.CSS_SELECTOR, "a.ds-dex-table-row")
        
        for row in rows[:20]: # Limit to top 10
            try:
                # Helper to safely get text
                def get_text(selector):
                    try:
                        return row.find_element(By.CSS_SELECTOR, selector).text.strip()
                    except NoSuchElementException:
                        return ""

                href = row.get_attribute('href')
                pair_address = href.split('/')[-1] if href else ''

                price_change_h24_text = get_text('.ds-dex-table-row-col-price-change-h24')
                
                token_data = {
                    "id": pair_address,
                    "tokenAddress": pair_address,
                    "name": get_text('.ds-dex-table-row-base-token-name-text'),
                    "symbol": get_text('.ds-dex-table-row-base-token-symbol'),
                    "priceUsd": parse_currency(get_text('.ds-dex-table-row-col-price')),
                    "pairAge": get_text('.ds-dex-table-row-col-pair-age'),
                    "volume": { "h24": parse_currency(get_text('.ds-dex-table-row-col-volume')) },
                    # Fix: Remove commas from price_change_h24_text before converting to float
                    "priceChange": { "h24": float(price_change_h24_text.replace('%', '').replace(',', '')) if price_change_h24_text else 0.0 },
                    "marketCap": parse_currency(get_text('.ds-dex-table-row-col-market-cap')),
                }
                
                # Only add if we have essential data
                if token_data["id"] and token_data["name"] and token_data["marketCap"] > 0:
                    scraped_tokens.append(token_data)

            except Exception as e:
                print(f"Error processing a row: {e}")
                continue # Move to the next row

    except TimeoutException:
        print("Timeout while waiting for page elements.")
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        print(f"Scraping finished. Found {len(scraped_tokens)} valid tokens.")
        driver.quit()
        
    return scraped_tokens