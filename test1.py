import json
import random
import re
import time
import undetected_chromedriver as uc
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver():
    """Initialize and return a configured undetected Chrome WebDriver."""
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")

    # Pass version_main to match your local Chrome (131)
    driver = uc.Chrome(options=options, version_main=131)
    return driver


def main():
    # --- CONFIGURATION FOR PAGES ---
    from_page = 158
    to_page = 159
    # -------------------------------

    # Step 1: Load the base URL from config.json
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            raw_base_url = config.get("url")

        if not raw_base_url:
            raise ValueError("The 'url' key is missing in config.json")

    except FileNotFoundError:
        print("Error: 'config.json' file not found. Please create it.")
        return
    except json.JSONDecodeError:
        print("Error: 'config.json' is not a valid JSON file.")
        return

    # Clean up base URL by removing any pre-existing page parameters (e.g., &page=157 or ?page=157)
    # This prevents duplicate/conflicting parameters like &page=157&page=158
    clean_base_url = re.sub(r"([?&])page=\d+", "", raw_base_url)
    
    # Ensure proper separator (? or &) for appending our clean page parameter
    if "?" in clean_base_url:
        separator = "&"
    else:
        separator = "?"

    # Step 2: Initialize the browser
    print("Initializing browser...")
    driver = setup_driver()

    all_extracted_data = []

    try:
        # Loop through the specified page range
        for page_num in range(from_page, to_page + 1):
            print(f"\n--- Processing Page {page_num} ---")

            # Construct the exact URL for the current page
            current_url = f"{clean_base_url}{separator}page={page_num}"

            print(f"Navigating to: {current_url}")
            driver.get(current_url)

            # Handle cookie banner only on the first page load
            if page_num == from_page:
                print("Checking for cookie consent banner...")
                try:
                    accept_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.ID, "truste-consent-button")
                        )
                    )
                    accept_button.click()
                    print("Successfully clicked 'I accept all cookies'.")
                except Exception:
                    print(
                        "Cookie banner not found or already accepted. Continuing..."
                    )

            # Wait for content cards to load
            print("Waiting for profile cards to load...")
            time.sleep(4)

            # Locate profile cards using your specific container XPath
            xpath_query = '//*[@id="app"]/main/div/div/div[2]//udex-tile[contains(@class, "pf-card-tile") or contains(@accessible-name, "Profile Card")]'
            cards = driver.find_elements(By.XPATH, xpath_query)

            # Fallback if specific XPath didn't return cards
            if not cards:
                print("Trying fallback XPath to locate profile tiles...")
                cards = driver.find_elements(By.TAG_NAME, "udex-tile")

            print(f"Found {len(cards)} profile cards on page {page_num}.")

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

            print(
                f"Successfully extracted {page_data_count} records from page {page_num}."
            )

            # If this is not the last page, add a random 15 to 20 second timeout to protect the server
            if page_num < to_page:
                wait_time = random.uniform(15, 20)
                print(
                    f"Waiting for {wait_time:.2f} seconds before moving to the next page..."
                )
                time.sleep(wait_time)

        # Step 3: Save all collected data across all pages to Excel
        if all_extracted_data:
            df = pd.DataFrame(all_extracted_data)
            excel_filename = f"profile_cards_pages_{from_page}_to_{to_page}.xlsx"
            df.to_excel(excel_filename, index=False)
            print(
                f"\n[SUCCESS] Saved a total of {len(all_extracted_data)} records to '{excel_filename}'."
            )
        else:
            print("\n[WARNING] No profile data found across the specified pages.")

        # Pause to let you view the final state before closing
        input("\nPress Enter to close the browser...")

    finally:
        # Step 4: Clean up and close the browser
        driver.quit()


if __name__ == "__main__":
    main()