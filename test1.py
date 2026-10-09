import json
import random
import re
import time
import undetected_chromedriver as uc
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


from helper_utils import get_installed_chrome_major_version


def setup_driver():
    """Initialize and return a configured undetected Chrome WebDriver with auto Chrome version detection."""
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")

    major_v = get_installed_chrome_major_version()
    if major_v:
        driver = uc.Chrome(options=options, version_main=major_v)
    else:
        try:
            driver = uc.Chrome(options=options)
        except Exception:
            driver = uc.Chrome()
    return driver


def run_get_links(from_page=158, to_page=159, log_func=print, stop_event=None, auto_close=False):
    """Extract profile links across a range of pages and save to Excel."""
    # Step 1: Load the base URL from config.json
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            raw_base_url = config.get("url")

        if not raw_base_url:
            raise ValueError("The 'url' key is missing in config.json")

    except FileNotFoundError:
        log_func("Error: 'config.json' file not found. Please create it.")
        return
    except json.JSONDecodeError:
        log_func("Error: 'config.json' is not a valid JSON file.")
        return

    # Clean up base URL by removing any pre-existing page parameters
    clean_base_url = re.sub(r"([?&])page=\d+", "", raw_base_url)
    
    # Ensure proper separator (? or &)
    if "?" in clean_base_url:
        separator = "&"
    else:
        separator = "?"

    # Step 2: Initialize the browser
    log_func("Initializing browser...")
    driver = setup_driver()

    all_extracted_data = []

    try:
        # Loop through the specified page range
        for page_num in range(from_page, to_page + 1):
            if stop_event and stop_event.is_set():
                log_func("[CANCELLED] Process stopped by user.")
                break

            log_func(f"\n--- Processing Page {page_num} ---")

            # Construct the exact URL for the current page
            current_url = f"{clean_base_url}{separator}page={page_num}"

            log_func(f"Navigating to: {current_url}")
            driver.get(current_url)

            # Handle cookie banner only on the first page load
            if page_num == from_page:
                log_func("Checking for cookie consent banner...")
                try:
                    accept_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.ID, "truste-consent-button")
                        )
                    )
                    accept_button.click()
                    log_func("Successfully clicked 'I accept all cookies'.")
                    # Give SAP page 2 seconds to initiate cookie reload if needed
                    time.sleep(2)
                except Exception:
                    log_func(
                        "Cookie banner not found or already accepted. Continuing..."
                    )

            if stop_event and stop_event.is_set():
                log_func("[CANCELLED] Process stopped by user.")
                break

            # Smart dynamic wait for profile cards to load (supports slow internet & cookie reload)
            log_func("Waiting for profile cards to load...")
            cards = []
            max_wait_seconds = 25
            start_time = time.time()
            xpath_query = '//*[@id="app"]/main/div/div/div[2]//udex-tile[contains(@class, "pf-card-tile") or contains(@accessible-name, "Profile Card")]'

            while (time.time() - start_time) < max_wait_seconds:
                if stop_event and stop_event.is_set():
                    break
                try:
                    found_cards = driver.find_elements(By.XPATH, xpath_query)
                    if not found_cards:
                        found_cards = driver.find_elements(By.TAG_NAME, "udex-tile")

                    # Check if valid cards with attributes are populated
                    valid_cards = [c for c in found_cards if (c.get_attribute("accessible-name") or c.get_attribute("href"))]
                    if valid_cards:
                        cards = valid_cards
                        break
                except Exception:
                    pass
                time.sleep(1.5)

            log_func(f"Found {len(cards)} profile cards on page {page_num}.")

            page_data_count = 0
            for card in cards:
                profile_name = card.get_attribute("accessible-name") or "N/A"
                profile_url = card.get_attribute("href") or "N/A"
                automation_id = card.get_attribute("automation-id") or "N/A"

                if profile_url != "N/A" or profile_name != "N/A":
                    all_extracted_data.append(
                        {
                            "Page": page_num,
                            "Profile Name": profile_name,
                            "Automation ID": automation_id,
                            "Profile URL": profile_url,
                        }
                    )
                    page_data_count += 1

            log_func(
                f"Successfully extracted {page_data_count} records from page {page_num}."
            )

            # If this is not the last page, add a random 15 to 20 second timeout to protect the server
            if page_num < to_page:
                if stop_event and stop_event.is_set():
                    log_func("[CANCELLED] Process stopped by user.")
                    break
                wait_time = random.uniform(15, 20)
                log_func(
                    f"Waiting for {wait_time:.2f} seconds before moving to the next page..."
                )
                time.sleep(wait_time)

        # Step 3: Save all collected data across all pages to Excel
        if all_extracted_data:
            df = pd.DataFrame(all_extracted_data)
            excel_filename = f"profile_cards_pages_{from_page}_to_{to_page}.xlsx"
            df.to_excel(excel_filename, index=False)
            log_func(
                f"\n[SUCCESS] Saved a total of {len(all_extracted_data)} records to '{excel_filename}'."
            )
        else:
            log_func("\n[WARNING] No profile data found across the specified pages.")

        if not auto_close:
            input("\nPress Enter to close the browser...")

    finally:
        # Step 4: Clean up and close the browser
        driver.quit()


def main():
    # --- CONFIGURATION FOR PAGES ---
    from_page = 158
    to_page = 159
    # -------------------------------
    run_get_links(from_page, to_page, log_func=print, auto_close=False)


if __name__ == "__main__":
    main()