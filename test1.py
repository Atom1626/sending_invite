import json
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
    # Step 1: Load the URL from config.json
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            target_url = config.get("url")

        if not target_url:
            raise ValueError("The 'url' key is missing in config.json")

    except FileNotFoundError:
        print("Error: 'config.json' file not found. Please create it.")
        return
    except json.JSONDecodeError:
        print("Error: 'config.json' is not a valid JSON file.")
        return

    # Step 2: Initialize the browser
    print("Initializing browser...")
    driver = setup_driver()

    try:
        # Step 3: Open the URL
        print(f"Navigating to: {target_url}")
        driver.get(target_url)

        # Step 4: Conditionally check for and click the cookie consent button
        print("Checking for cookie consent banner...")
        try:
            accept_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "truste-consent-button"))
            )
            accept_button.click()
            print("Successfully clicked 'I accept all cookies'.")
        except Exception:
            print("Cookie banner not found. Continuing without clicking.")

        # Step 5: Wait for the main card container/elements to load
        print("Waiting for profile cards to load...")
        # Giving it a moment to ensure cards render after login/cookies
        time.sleep(3) 

        # Step 6: Locate all matching profile card elements using XPath
        # This targets the tile elements inside the container path you specified
        xpath_query = '//*[@id="app"]/main/div/div/div[2]//udex-tile[contains(@class, "pf-card-tile") or contains(@accessible-name, "Profile Card")]'
        
        # Alternatively, a broader search using the container root if elements load dynamically:
        # container_xpath = '//*[@id="app"]/main/div/div/div[2]'
        
        cards = driver.find_elements(By.XPATH, xpath_query)
        
        # If the precise XPath returns nothing, let's try a fallback targeting any udex-tile inside the main view
        if not cards:
            print("Trying fallback XPath to locate profile tiles...")
            cards = driver.find_elements(By.TAG_NAME, "udex-tile")

        print(f"Found {len(cards)} profile cards.")

        extracted_data = []

        for card in cards:
            # Extract the 'accessible-name' (Profile name/card info)
            profile_name = card.get_attribute("accessible-name") or "N/A"
            
            # Extract the 'href' attribute (URL)
            profile_url = card.get_attribute("href") or "N/A"
            
            # Optional: also grab automation-id if helpful
            automation_id = card.get_attribute("automation-id") or "N/A"

            if profile_url != "N/A" or profile_name != "N/A":
                extracted_data.append({
                    "Profile Name": profile_name,
                    "Automation ID": automation_id,
                    "Profile URL": profile_url
                })

        # Step 7: Save to Excel using Pandas
        if extracted_data:
            df = pd.DataFrame(extracted_data)
            excel_filename = "profile_cards.xlsx"
            df.to_excel(excel_filename, index=False)
            print(f"Successfully saved {len(extracted_data)} records to '{excel_filename}'.")
        else:
            print("No matching profile data found to save.")

        # Pause to let you view the page afterward
        input("Press Enter to close the browser...")

    finally:
        # Step 8: Clean up and close the browser
        driver.quit()


if __name__ == "__main__":
    main()